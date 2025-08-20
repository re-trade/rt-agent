mod config;
mod service;

use std::net::SocketAddr;

use config::CONFIG;
use service::identity::{IdentityService, IdentityServiceServer};
use tonic::transport::Server;
use tracing::level_filters::LevelFilter;
use tracing_subscriber::{
    EnvFilter, fmt::time::ChronoLocal, layer::SubscriberExt, util::SubscriberInitExt,
};

#[tokio::main]
async fn main() {
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::fmt::layer()
                .pretty()
                .with_timer(ChronoLocal::rfc_3339()),
        )
        .with(
            EnvFilter::builder()
                .with_default_directive(LevelFilter::INFO.into())
                .from_env_lossy(),
        )
        .init();

    let addr = SocketAddr::new([0, 0, 0, 0].into(), CONFIG.port);

    tracing::info!("Starting ...");

    Server::builder()
        .add_service(IdentityServiceServer::new(IdentityService))
        .serve(addr)
        .await
        .unwrap();
}
