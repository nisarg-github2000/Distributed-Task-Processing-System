import { PagesComponent } from './pages.component';
import { BrowserModule } from '@angular/platform-browser';
import { PagesRoutingModule } from './pages-routing.module';
import { RouterModule } from '@angular/router';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { SharedService } from '../shared.service';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { ForgotPasswordPageComponent } from './forgot-password/forgot-password.component';
import { RegisterPageComponent } from './register/register.component';
import { LoginComponent } from './login/login.component';
import { CommonModule } from '@angular/common';
import { ProductListComponent } from '../components/product-list/product-list.component';
import { SpinnerModule } from '../shared/spinner/spinner.module';
import { CreateProjectComponent } from '../components/create-project/create-project.component';
import { ShareIconsModule } from 'ngx-sharebuttons/icons';
import { ShareButtonsModule } from 'ngx-sharebuttons/buttons';


@NgModule({
  declarations: [
    PagesComponent,
    ProductListComponent,
    RegisterPageComponent,
    ForgotPasswordPageComponent,
    LoginComponent,
    CreateProjectComponent,
  ],
  imports: [
    CommonModule,
    PagesRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    NgbModule,
    SpinnerModule,
    ShareButtonsModule,
    ShareIconsModule,
  ],
  providers: [
    SharedService
  ],
  bootstrap: []
})
export class PagesModule { }
