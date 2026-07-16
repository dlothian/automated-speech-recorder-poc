import { ApplicationConfig } from '@angular/core';
import * as core from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
/* highlight-start import-provide-auth0 */
import { provideAuth0 } from '@auth0/auth0-angular';
/* highlight-end import-provide-auth0 */

export const appConfig: ApplicationConfig = {
  providers: [
    (core as any).provideBrowserGlobalErrorListeners?.() || [], // Conditional for Angular v19
    provideRouter(routes),
    /* highlight-start provider-config */
    provideAuth0({
      domain: "dev-qioor1nubb5vu3uw.ca.auth0.com",
      clientId: "FDxgeYBhbO7dhVxqehSFgOvV1ApXKEMp",
      authorizationParams: {
        redirect_uri: window.location.origin,
      },
    }),
    /* highlight-end provider-config */
  ],
};
