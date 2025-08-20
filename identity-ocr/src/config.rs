use std::sync::LazyLock;

use serde::Deserialize;

const fn default_port() -> u16 {
    5000
}

fn default_model() -> String {
    "gpt-4o-mini".to_string()
}

#[derive(Debug, Deserialize)]
pub struct Config {
    #[serde(default = "default_port")]
    pub port: u16,

    pub openai_key: String,

    #[serde(default = "default_model")]
    pub model: String,
}

pub static CONFIG: LazyLock<Config> = LazyLock::new(|| {
    ::config::Config::builder()
        .add_source(
            ::config::Environment::default()
                .try_parsing(true)
                .separator("__"),
        )
        .build()
        .unwrap()
        .try_deserialize()
        .unwrap()
});
