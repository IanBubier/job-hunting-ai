// Minimal UI helpers for the frontend

class SearchForm {
  constructor(formElement) {
    this.form = formElement;
    this.fields = {
      skills: '',
      keywords: '',
      location: '',
      experience: 'entry'
    };
  }

  getFormData() {
    const fd = new FormData(this.form);
    return {
      skills: fd.get('skills') ? fd.get('skills').split(',').map(s => s.trim()).filter(Boolean) : [],
      keywords: fd.get('keywords') || '',
      location: fd.get('location') || '',
      experience: fd.get('experience') || 'entry',
      max_results: parseInt(fd.get('max_results') || '20', 10)
    };
  }

  validate() {
    const data = this.getFormData();
    return data.skills.length > 0 && data.keywords.length >= 3;
  }

  handleSubmit(callback) {
    this.form.addEventListener('submit', e => {
      e.preventDefault();
      if (!this.validate()) {
        callback(new Error('Validation failed'));
        return;
      }
      callback(null, this.getFormData());
    });
  }
}

class ResultsDisplay {
  constructor(containerElement) {
    this.container = containerElement;
    this.jobs = [];
  }

  render(jobs) {
    this.jobs = jobs || [];
    this.container.innerHTML = '';
    if (this.jobs.length === 0) {
      this.container.innerHTML = '<p>No jobs found</p>';
      return;
    }

    const list = document.createElement('div');
    list.className = 'job-list';

    this.jobs.forEach(j => {
      const card = document.createElement('div');
      card.className = 'job-card';
      card.innerHTML = `
        <h3>${j.title} <small>${j.match_score || ''}%</small></h3>
        <p><strong>${j.company}</strong> — ${j.location}</p>
        <p>${j.description ? j.description.substring(0,200) + '...' : ''}</p>
        <a href="${j.url || '#'}" target="_blank">View</a>
      `;
      list.appendChild(card);
    });

    this.container.appendChild(list);
  }

  showLoading() {
    this.container.innerHTML = '<p>Loading...</p>';
  }

  showError(message) {
    this.container.innerHTML = `<p class="error">${message}</p>`;
  }
}

// Export for other modules (if using bundler)
window.SearchForm = SearchForm;
window.ResultsDisplay = ResultsDisplay;

// Skill input + button interaction
document.addEventListener('DOMContentLoaded', () => {
  const addSkillBtn = document.getElementById('add-skill-btn');
  const skillsInput = document.getElementById('skills-input');
  const chipsContainer = document.querySelector('.chips');

  if (!addSkillBtn || !skillsInput || !chipsContainer) return;

  addSkillBtn.addEventListener('click', () => {
    const skill = skillsInput.value.trim();
    if (skill) {
      const chip = document.createElement('span');
      chip.className = 'chip';
      chip.textContent = skill;

      // Add remove "x" for chip deletion
      const removeBtn = document.createElement('button');
      removeBtn.className = 'remove-chip';
      removeBtn.textContent = '×';
      removeBtn.addEventListener('click', () => chip.remove());
      chip.appendChild(removeBtn);

      chipsContainer.appendChild(chip);
      skillsInput.value = '';
    }
  });
});
