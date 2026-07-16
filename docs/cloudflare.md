## Cloudflare Setup

1. Go to https://dash.cloudflare.com/profile/api-tokens
2. Click "Create Token"
3. Click "Create Custom Token"
4. Name it: `<your-project-name>-deploy`
5. Add these permissions:

   | Permission                      | Level |
   | ------------------------------- | ----- |
   | Account → Cloudflare Pages      | Edit  |
   | Account → Account Settings      | Read  |
   | Account → Workers Scripts       | Edit  |
   | Account → Workers KV Storage    | Edit  |
   | Account → Workers R2 Storage    | Edit  |
   | Account → Workers Routes        | Edit  |
   | Account → Workers Observability | Edit  |

6. Click "Continue to summary" → "Create Token"
7. Copy the token
8. In your GitHub repo: Settings → Secrets → Actions → New secret
   - Name: `CLOUDFLARE_API_TOKEN`, Value: (paste token)
   - Name: `CLOUDFLARE_ACCOUNT_ID`, Value: (your account ID from the dashboard)
