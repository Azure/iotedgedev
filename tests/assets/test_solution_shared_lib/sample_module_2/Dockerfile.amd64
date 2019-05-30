FROM microsoft/dotnet:2.1-sdk AS build-env

COPY ./libs /app/libs
COPY ./sample_module_2/*.csproj /app/sample_module_2/
COPY ./sample_module_2 /app/sample_module_2

WORKDIR /app/sample_module_2
RUN dotnet restore
RUN dotnet publish -c Release -o /app/out

FROM microsoft/dotnet:2.1-runtime-stretch-slim
WORKDIR /app
COPY --from=build-env /app/out ./

RUN useradd -ms /bin/bash moduleuser
USER moduleuser

ENTRYPOINT ["dotnet", "sample_module_2.dll"]