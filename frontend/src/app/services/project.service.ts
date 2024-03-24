import { HttpClient } from '@angular/common/http';
import { Injectable } from "@angular/core";
import { environment } from '../../environments/environment';
import { AuthenticationService } from './auth.service';

@Injectable({
  providedIn: "root"
})
export class ProjectService {
  constructor(private http: HttpClient, private authService: AuthenticationService) { }
  create(payload) {
    return this.http.post(environment.kernel_url + "/api/v1/job_executor/async?executor=standard", {
      ...payload,
      "user_id": this.authService?.currentUser?.uid
    });
  }
  getMyProjects() {
    return this.http.get(environment.dataservice_url + "/job/" + this.authService?.currentUser?.uid);
  }
}