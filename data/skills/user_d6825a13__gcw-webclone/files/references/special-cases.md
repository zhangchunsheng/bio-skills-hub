# Special cases

Use these playbooks only when reconnaissance finds the matching condition.

## Text baked into GLTF or GLB geometry

Visible words in a 3D scene may be mesh geometry rather than JavaScript, HTML or texture text. Confirm the model owner and inspect the asset before searching the application repeatedly for a string.

When replacement is required, use Blender to generate a repeatable geometry baseline against the reference bounds:

```text
blender --background --python <skill-root>/scripts/blender_replace_text.py -- \
  --reference <old-model.gltf> --text "NEW WORD" --output <new-model.glb> \
  --font <font-file.ttf>
```

This does not recreate hand-drawn lettering automatically. Validate:

- bounds, origin and camera framing
- material assignment and lighting response
- desktop and mobile overlap
- pointer or physics response
- font and model redistribution rights

Blender is optional and required only for this playbook.
