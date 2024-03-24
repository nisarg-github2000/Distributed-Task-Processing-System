import { FormGroup, FormControl, Validators, FormArray, FormBuilder } from '@angular/forms';
import { Component, Output, EventEmitter } from "@angular/core";
import { NgbModal } from "@ng-bootstrap/ng-bootstrap";
import { ProjectService } from './../../services';

@Component({
  selector: "create-project",
  templateUrl: "./create-project.component.html"
})
export class CreateProjectComponent {
  constructor(private modalService: NgbModal, private projectService: ProjectService, public fb: FormBuilder) { }
  @Output() projectDetails = new EventEmitter();
  createProjectForm = new FormGroup({
    job_name: new FormControl('', [Validators.required]),
    description: new FormControl('',),
    estimated_time: new FormControl(30, [Validators.required]),
  });
  open(createProject) {
    this.modalService.open(createProject);
  }
  submit() {
    this.projectService.create(this.createProjectForm.value).toPromise().then((data) => {
      console.log(data);
      this.modalService.dismissAll();
    })
  }
}