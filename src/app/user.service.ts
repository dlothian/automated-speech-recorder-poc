import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
    providedIn: 'root'
})
export class UserService {

    private apiUrl = 'https://auth0-angular-api.delaney-lothian.workers.dev/';

    constructor(private http: HttpClient) { }

    saveUser(user: any) {
        return this.http.post(
            `${this.apiUrl}/users`,
            {
                sub: user.sub,
                email: user.email,
                name: user.name,
                picture: user.picture
            }
        );
    }
}