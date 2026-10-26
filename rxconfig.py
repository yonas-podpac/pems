import reflex as rx

config = rx.Config(
    app_name="pems",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        # api_url=""
    ]
)