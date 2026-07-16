import { Component } from '@angular/core';
import { AuthService } from '@auth0/auth0-angular';
import { AsyncPipe, JsonPipe } from '@angular/common';

@Component({
  selector: 'app-protected',
  imports: [AsyncPipe, JsonPipe],
  templateUrl: './protected.html'
})
export class ProtectedComponent {
  constructor(public auth: AuthService) { }
}