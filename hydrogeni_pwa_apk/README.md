# HydrogenI BoxTwin APK Flutter

Aplicativo Android Flutter com WebView para abrir o PWA operacional do BoxTwin.

## O que ele faz

- Abre o app do Railway:
  `https://hydrogeni-boxtwin-production.up.railway.app/app`
- Permite informar a URL local do Raspberry:
  `http://boxtwin.local:5000/app`
- Mantém o PWA e as funcionalidades atuais sem reescrever as telas.

## Gerar APK

Instale o Flutter e o Android Studio/SDK. Depois, dentro desta pasta:

```powershell
flutter pub get
flutter build apk --release
```

O APK será gerado em:

```text
build/app/outputs/flutter-apk/app-release.apk
```

## Teste rápido

```powershell
flutter run
```

Para usar o Raspberry, o celular precisa estar na mesma rede local do BoxNode.
