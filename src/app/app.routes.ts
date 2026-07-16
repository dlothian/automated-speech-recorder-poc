import { Routes } from '@angular/router';
import { authGuard } from './auth-guard';
import { ProtectedComponent } from './protected/protected';

export const routes: Routes = [
    {
        path: 'protected',
        component: ProtectedComponent,
        canActivate: [authGuard]
    }
];