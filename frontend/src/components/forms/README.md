# Form Components

This directory contains reusable form components with built-in validation using React Hook Form and Zod.

## Components

### SkillsInput
Tag input component for skills with validation.

```tsx
import { SkillsInput } from '../components/forms';
import { useForm } from 'react-hook-form';

const { register, formState: { errors } } = useForm();

<SkillsInput
  skills={skills}
  onSkillsChange={setSkills}
  register={register('skills')}
  error={errors.skills}
  placeholder="Type a skill and press Enter"
  maxSkills={10}
/>
```

### RIASECInterestSelector
Selector for RIASEC interest categories with sliders (0-7 scale).

```tsx
import { RIASECInterestSelector } from '../components/forms';

<RIASECInterestSelector
  interests={interests}
  onInterestsChange={setInterests}
  setValue={setValue}
  error={errors.interests}
/>
```

### ValueSlider
Slider component for work values (0-7 scale).

```tsx
import { ValueSlider } from '../components/forms';

<ValueSlider
  label="Impact"
  value={impact}
  onChange={setImpact}
  min={0}
  max={7}
  step={0.1}
  error={errors.impact}
  description="How important is making an impact?"
/>
```

### FileUpload
File upload component with drag & drop and validation.

```tsx
import { FileUpload } from '../components/forms';

<FileUpload
  file={file}
  onFileChange={setFile}
  register={register('file')}
  error={errors.file}
  accept=".pdf,.docx,.txt"
  showPreview={true}
/>
```

### CareerSelector
Searchable career selector component.

```tsx
import { CareerSelector } from '../components/forms';

<CareerSelector
  careers={careerCatalog}
  selectedCareerId={careerId}
  onCareerChange={setCareerId}
  register={register('careerId')}
  error={errors.careerId}
  showSearch={true}
  required={true}
/>
```

## Usage with React Hook Form

All components are designed to work seamlessly with React Hook Form:

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { recommendationRequestSchema } from '../../schemas/validation';

const { register, handleSubmit, formState: { errors }, setValue, watch } = useForm({
  resolver: zodResolver(recommendationRequestSchema),
  defaultValues: {
    skills: [],
    interests: {},
    work_values: { impact: 3.5, stability: 3.5, flexibility: 3.5 },
    top_n: 5,
    use_ml: true,
  },
});

const onSubmit = (data) => {
  console.log(data);
};
```

## Validation Schemas

Validation schemas are defined in `src/schemas/validation.ts` and match backend validation rules:

- `skillsSchema` - Skills validation (non-empty strings, max 100 chars)
- `interestsSchema` - Interests validation (RIASEC categories or text)
- `interestsRecordSchema` - Interests as record (for recommendations)
- `valuesSchema` - Values validation (0-7 range)
- `constraintsSchema` - Constraints validation (proper structure)
- `fileSchema` - File upload validation (size, type)
- `intakeRequestSchema` - Complete intake request schema
- `recommendationRequestSchema` - Complete recommendation request schema






