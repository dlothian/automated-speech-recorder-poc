import { Component } from '@angular/core';
import { AuthService } from '@auth0/auth0-angular';
import { AsyncPipe, JsonPipe, CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';


@Component({
  selector: 'app-protected',
  imports: [AsyncPipe, JsonPipe, CommonModule],
  templateUrl: './protected.html'
})
export class ProtectedComponent {
  constructor(
    public auth: AuthService,
    private http: HttpClient
  ) { }

  selectedFile?: File;

  workerUrl = 'https://auth0-angular-api.delaney-lothian.workers.dev/audio';


  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;

    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];

      console.log("Selected file:", this.selectedFile);

      this.uploadAudio();
    }
  }


  async uploadAudio() {
    if (!this.selectedFile) {
      return;
    }

    const token = await firstValueFrom(
      this.auth.getAccessTokenSilently()
    );

    const formData = new FormData();

    formData.append(
      "file",
      this.selectedFile,
      this.selectedFile.name
    );

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    this.http.post(
      this.workerUrl,
      formData,
      { headers }
    )
      .subscribe({
        next: response => {
          console.log("Upload successful:", response);
        },
        error: error => {
          console.error("Upload failed:", error);
        }
      });
  }
}
