FROM microsoft/dotnet:2.1-sdk AS build-env

COPY ./libs /app/libs
COPY ./modules/sample_module/*.csproj /app/modules/sample_module/
COPY ./modules/sample_module /app/modules/sample_module

WORKDIR /app/modules/sample_module
RUN dotnet restore
RUN dotnet publish -c Release -o /app/out

FROM microsoft/dotnet:2.1-runtime-nanoserver-1803
WORKDIR /app
COPY --from=build-env /app/out ./

ENTRYPOINT ["dotnet", "sample_module.dll"]