import { Component } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';

/* highlight-start import-auth0 */
import { inject } from '@angular/core';
import { AuthService } from '@auth0/auth0-angular';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
/* highlight-end import-auth0 */

@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet,
    /* highlight-start imports-common */
    CommonModule,
    /* highlight-end imports-common */
    RouterLink,
  ],
  templateUrl: './app.html',
})
export class App {
  protected readonly window = window;

  protected auth = inject(AuthService);
  protected route = inject(ActivatedRoute);
}
