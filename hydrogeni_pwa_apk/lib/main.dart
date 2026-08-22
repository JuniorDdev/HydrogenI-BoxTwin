import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:webview_flutter_android/webview_flutter_android.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const HydrogenIApp());
}

class HydrogenIApp extends StatelessWidget {
  const HydrogenIApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'HydrogenI BoxTwin',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF18D4FF),
          brightness: Brightness.dark,
        ),
        scaffoldBackgroundColor: const Color(0xFF101314),
        useMaterial3: true,
      ),
      home: const StartPage(),
    );
  }
}

class StartPage extends StatefulWidget {
  const StartPage({super.key});

  @override
  State<StartPage> createState() => _StartPageState();
}

class _StartPageState extends State<StartPage> {
  static const cloudUrl = 'https://hydrogeni-boxtwin-production.up.railway.app/app';
  final localController = TextEditingController(text: 'http://boxtwin.local:5000/app');

  @override
  void dispose() {
    localController.dispose();
    super.dispose();
  }

  void open(String url) {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => BoxTwinWebView(initialUrl: url)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(22),
          children: [
            const SizedBox(height: 18),
            Container(
              padding: const EdgeInsets.all(22),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(28),
                border: Border.all(color: const Color(0x333EDCFF)),
                gradient: const LinearGradient(
                  colors: [Color(0xFF061426), Color(0xFF0B2D4A)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                boxShadow: const [
                  BoxShadow(color: Color(0x551769FF), blurRadius: 38, offset: Offset(0, 18)),
                ],
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'HYDROGENI',
                    style: TextStyle(
                      color: Color(0xFF18D4FF),
                      fontSize: 12,
                      fontWeight: FontWeight.w900,
                      letterSpacing: 2.8,
                    ),
                  ),
                  SizedBox(height: 12),
                  Text(
                    'BoxTwin Operacional',
                    style: TextStyle(fontSize: 32, fontWeight: FontWeight.w900, height: 1.05),
                  ),
                  SizedBox(height: 12),
                  Text(
                    'Acesse o painel PWA do Railway ou conecte diretamente ao Raspberry na rede local.',
                    style: TextStyle(color: Color(0xFFB7C8D5), height: 1.5),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            FilledButton(
              onPressed: () => open(cloudUrl),
              style: FilledButton.styleFrom(
                backgroundColor: const Color(0xFF1769FF),
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              ),
              child: const Text('Conectar Railway'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: localController,
              keyboardType: TextInputType.url,
              decoration: InputDecoration(
                labelText: 'URL local do Raspberry',
                hintText: 'http://boxtwin.local:5000/app',
                filled: true,
                fillColor: const Color(0xFF151C22),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
              ),
            ),
            const SizedBox(height: 12),
            OutlinedButton(
              onPressed: () => open(localController.text.trim()),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              ),
              child: const Text('Conectar Raspberry/local'),
            ),
            const SizedBox(height: 20),
            const Text(
              'Dica: para usar o Raspberry, o celular precisa estar na mesma rede Wi‑Fi/local do BoxNode.',
              style: TextStyle(color: Color(0xFF8DA5BA), height: 1.45),
            ),
          ],
        ),
      ),
    );
  }
}

class BoxTwinWebView extends StatefulWidget {
  const BoxTwinWebView({required this.initialUrl, super.key});

  final String initialUrl;

  @override
  State<BoxTwinWebView> createState() => _BoxTwinWebViewState();
}

class _BoxTwinWebViewState extends State<BoxTwinWebView> {
  late final WebViewController controller;
  var progress = 0;
  var title = 'BoxTwin';

  @override
  void initState() {
    super.initState();
    final params = const PlatformWebViewControllerCreationParams();
    controller = WebViewController.fromPlatformCreationParams(params)
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0xFF101314))
      ..setNavigationDelegate(
        NavigationDelegate(
          onProgress: (value) => setState(() => progress = value),
          onPageStarted: (_) => setState(() => progress = 0),
          onPageFinished: (_) async {
            final pageTitle = await controller.getTitle();
            if (mounted) {
              setState(() {
                progress = 100;
                title = pageTitle ?? 'BoxTwin';
              });
            }
          },
        ),
      )
      ..loadRequest(Uri.parse(widget.initialUrl));

    if (controller.platform is AndroidWebViewController) {
      AndroidWebViewController.enableDebugging(false);
      (controller.platform as AndroidWebViewController).setMediaPlaybackRequiresUserGesture(false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(title, overflow: TextOverflow.ellipsis),
        actions: [
          IconButton(
            tooltip: 'Atualizar',
            onPressed: () => controller.reload(),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: Column(
        children: [
          if (progress < 100)
            LinearProgressIndicator(
              value: progress / 100,
              color: const Color(0xFF18D4FF),
              backgroundColor: const Color(0xFF061426),
            ),
          Expanded(child: WebViewWidget(controller: controller)),
        ],
      ),
    );
  }
}
