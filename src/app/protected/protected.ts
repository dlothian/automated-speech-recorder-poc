import { Component } from '@angular/core';
import { AuthService } from '@auth0/auth0-angular';
import { AsyncPipe, JsonPipe, CommonModule } from '@angular/common';

@Component({
  selector: 'app-protected',
  imports: [AsyncPipe, JsonPipe, CommonModule],
  templateUrl: './protected.html'
})
export class ProtectedComponent {
  constructor(public auth: AuthService) { }

  selectedFile?: File;


  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;

    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];

      // Later:
      // upload this.selectedFile to your Worker
      console.log("Uploaded file:", this.selectedFile);
    }
  }
}