from setuptools import setup, find_packages

setup(
    name="microservices-shared",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.5.0",
        "aio-pika>=9.3.1",
        "opentelemetry-api>=1.21.0",
        "opentelemetry-sdk>=1.21.0",
        "opentelemetry-exporter-otlp-proto-http>=1.21.0",
        "opentelemetry-instrumentation-fastapi>=0.42b0",
        "opentelemetry-instrumentation-sqlalchemy>=0.42b0",
        "opentelemetry-instrumentation-aio-pika>=0.42b0",
    ],
    python_requires=">=3.11",
)
