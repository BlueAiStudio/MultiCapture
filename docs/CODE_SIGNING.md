# Code signing

Why: Windows SmartScreen warns about downloaded programs that are not signed by a known publisher.

## Microsoft Store version

The Store signs the MSIX package with Microsoft's certificate. Nothing to do here. See [STORE.md](STORE.md).

## GitHub download (MultiCapture.exe): Azure Artifact Signing

The workflow `.github/workflows/build.yml` signs `dist\MultiCapture.exe` with
[Azure Artifact Signing](https://learn.microsoft.com/azure/artifact-signing/) (formerly "Trusted Signing")
on pushes to `main` and on release tags. The step is skipped while the settings below are missing, so the
build keeps working unsigned.

Repository settings → **Secrets and variables → Actions**:

| Kind | Name | Value |
|---|---|---|
| Secret | `AZURE_TENANT_ID` | Directory (tenant) ID of the app registration |
| Secret | `AZURE_CLIENT_ID` | Application (client) ID of the app registration |
| Secret | `AZURE_CLIENT_SECRET` | Client secret value of the app registration |
| Variable | `SIGNING_ENDPOINT` | Account endpoint, e.g. `https://eus.codesigning.azure.net/` |
| Variable | `SIGNING_ACCOUNT` | Artifact Signing account name |
| Variable | `SIGNING_PROFILE` | Certificate profile name (Public Trust) |

The app registration needs the role **Artifact Signing Certificate Profile Signer**
(older name: *Trusted Signing Certificate Profile Signer*) on the signing account.

Check: the "Show signature" step of the build prints `Status : Valid` and the signer.

Note: SmartScreen reputation is built per certificate over time. A newly signed exe may still show the
warning for a while, but with the publisher's verified name instead of "Unknown publisher".
