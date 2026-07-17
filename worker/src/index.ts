const corsHeaders = {
    "Access-Control-Allow-Origin": "https://auth0-angular.pages.dev",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Authorization, Content-Type",
};

export default {
    async fetch(request: Request, env: Env) {

        if (request.method === "OPTIONS") {
            return new Response(null, {
                status: 204,
                headers: corsHeaders,
            });
        }

        if (request.method === "POST" && new URL(request.url).pathname === "/users") {

            const user = await request.json() as {
                sub: string;
                email: string;
                name: string;
                picture: string;
            };

            await env.DB
                .prepare(`
          INSERT OR IGNORE INTO users
          (auth0_id, email, name, picture)
          VALUES (?, ?, ?, ?)
        `)
                .bind(
                    user.sub,
                    user.email,
                    user.name,
                    user.picture
                )
                .run();

            return Response.json(
                { success: true },
                {
                    headers: corsHeaders,
                }
            );

        }

        return new Response("Not found", {
            status: 404,
            headers: corsHeaders,
        });

    }
};