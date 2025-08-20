mod proto {
    tonic::include_proto!("identity");
}

use async_openai::{
    config::OpenAIConfig,
    types::{
        ChatCompletionRequestMessageContentPartImageArgs,
        ChatCompletionRequestMessageContentPartTextArgs, ChatCompletionRequestSystemMessage,
        ChatCompletionRequestUserMessageArgs, CreateChatCompletionRequestArgs, ImageDetail,
        ImageUrlArgs, ResponseFormat, ResponseFormatJsonSchema,
    },
    Client,
};
pub use identity_service_server::IdentityServiceServer;
use proto::{identity_service_server, IdentityCard, IdentityCardRequest, IdentityCardResponse};
use schemars::schema_for;
use tonic::{Request, Response, Status};

use crate::config::CONFIG;

const SYSTEM_PROMPT: &str = "You are an assistance in extracting identity card information from image. Make a field empty if you cant find information about it.";
const DEFAULT_PROMPT: &str = "Extract data from this identity card";

#[derive(Default)]
pub struct IdentityService;

#[tonic::async_trait]
impl identity_service_server::IdentityService for IdentityService {
    async fn process_identity_card(
        &self,
        request: Request<IdentityCardRequest>,
    ) -> Result<Response<IdentityCardResponse>, Status> {
        let schema = schema_for!(IdentityCard);
        let mut schema_value = serde_json::to_value(&schema).expect("Schema build must never fail");
        if let Some(obj) = schema_value.as_object_mut() {
            obj.insert("additionalProperties".to_string(), serde_json::json!(false));
        }
        let response_format = ResponseFormat::JsonSchema {
            json_schema: ResponseFormatJsonSchema {
                description: None,
                name: "identity_card".into(),
                schema: Some(schema_value),
                strict: Some(true),
            },
        };
        let messages = vec![
            ChatCompletionRequestSystemMessage::from(SYSTEM_PROMPT).into(),
            ChatCompletionRequestUserMessageArgs::default()
                .content(vec![
                    ChatCompletionRequestMessageContentPartTextArgs::default()
                        .text(DEFAULT_PROMPT)
                        .build()
                        .expect("This must never fail")
                        .into(),
                    ChatCompletionRequestMessageContentPartImageArgs::default()
                        .image_url(
                            ImageUrlArgs::default()
                                .url(request.into_inner().base64_image)
                                .detail(ImageDetail::High)
                                .build()
                                .expect("This must never fail"),
                        )
                        .build()
                        .expect("This must never fail")
                        .into(),
                ])
                .build()
                .expect("This must never fail")
                .into(),
        ];
        let request = CreateChatCompletionRequestArgs::default()
            .model(&CONFIG.model)
            .messages(messages)
            .response_format(response_format)
            .build()
            .expect("This must never fail");

        let client =
            Client::with_config(OpenAIConfig::new().with_api_key(CONFIG.openai_key.clone()));
        let response = match client.chat().create(request).await {
            Ok(request) => request,
            Err(error) => {
                tracing::error!(?error, "Failed to call openai model");

                return Ok(Response::new(IdentityCardResponse {
                    message: "Failed to extract identity card information".to_string(),
                    card: None,
                    success: false,
                }));
            }
        };

        for choice in response.choices {
            if let Some(content) = choice.message.content {
                let card = match serde_json::from_str::<IdentityCard>(&content) {
                    Ok(card) => card,
                    Err(error) => {
                        tracing::error!(?error, "Model return invalid structure");
                        continue;
                    }
                };

                return Ok(Response::new(IdentityCardResponse {
                    message: String::new(),
                    card: Some(card),
                    success: true,
                }));
            }
        }

        tracing::error!("Response contain no valid choice");
        return Ok(Response::new(IdentityCardResponse {
            message: "Failed to extract identity card information".to_string(),
            card: None,
            success: false,
        }));
    }
}
