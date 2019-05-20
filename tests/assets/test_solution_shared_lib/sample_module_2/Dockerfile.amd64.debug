FROM microsoft/dotnet:2.1-runtime-stretch-slim AS base

RUN apt-get update && \
    apt-get install -y --no-install-recommends unzip procps && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash moduleuser
USER moduleuser
RUN curl -sSL https://aka.ms/getvsdbgsh | bash /dev/stdin -v latest -l ~/vsdbg

FROM microsoft/dotnet:2.1-sdk AS build-env

COPY ./libs /app/libs
COPY ./sample_module_2/*.csproj /app/sample_module_2/
COPY ./sample_module_2 /app/sample_module_2

WORKDIR /app/sample_module_2
RUN dotnet restore
RUN dotnet publish -c Debug -o /app/out

FROM base
WORKDIR /app
COPY --from=build-env /app/out ./

ENTRYPOINT ["dotnet", "sample_module_2.dll"]