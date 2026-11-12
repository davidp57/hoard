// Feasibility spike for the native Hoard client (BL-104).
//
// Deliberately minimal and disposable: this exists to answer three questions —
// does libmpv ship inside the bundle, does hardware decoding actually engage,
// and can we type without the Steam keyboard — not to be the client's
// foundation.
//
// It is meant to be run in Steam Deck Gaming Mode, where there is no terminal:
// every measurement is taken by the app itself and shown on screen, and every
// control is reachable with the D-pad (Steam Input maps it onto arrow keys).

import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:media_kit/media_kit.dart';
import 'package:media_kit_video/media_kit_video.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  MediaKit.ensureInitialized();
  runApp(const SpikeApp());
}

// ── CPU sampling ──────────────────────────────────────────────────────────────

/// Process CPU time, in seconds, read from /proc/self/stat.
///
/// This is a CUMULATIVE counter. Dividing it by uptime would describe the
/// average since launch, not the load right now — so callers must always take
/// the difference between two samples over a known interval.
double _cpuSecondsUsed() {
  final stat = File('/proc/self/stat').readAsStringSync();
  // Skip up to the comm field, which is parenthesised and may contain spaces.
  final fields = stat.substring(stat.lastIndexOf(')') + 2).split(' ');
  final utime = int.parse(fields[11]); // field 14 overall
  final stime = int.parse(fields[12]); // field 15 overall
  return (utime + stime) / 100.0; // USER_HZ is 100 on every Linux we target
}

// ── API client ────────────────────────────────────────────────────────────────

/// Thin wrapper over the endpoints the spike needs. Paths are relative to
/// MEDIA_ROOT, exactly as `/api/files` returns them.
///
/// The server may require HTTP Basic (HOARD_AUTH_USER / HOARD_AUTH_PASS on the
/// container). Credentials come from the launcher, because in Gaming Mode
/// there may be no way to type them — which is the very thing under test.
class HoardApi {
  HoardApi(this.baseUrl);

  final String baseUrl;

  /// Built once. Empty when the launcher supplies no credentials, in which
  /// case every request goes out unauthenticated, as before.
  static final Map<String, String> authHeader = _buildAuthHeader();

  static Map<String, String> _buildAuthHeader() {
    final user = Platform.environment['HOARD_USER'] ?? '';
    final pass = Platform.environment['HOARD_PASS'] ?? '';
    if (user.isEmpty || pass.isEmpty) return const {};
    final token = base64Encode(utf8.encode('$user:$pass'));
    return {'Authorization': 'Basic $token'};
  }

  static bool get authConfigured => authHeader.isNotEmpty;

  Uri _uri(String route, [Map<String, String>? query]) =>
      Uri.parse('$baseUrl$route').replace(queryParameters: query);

  /// Direct file URL handed to mpv — no transcoding, server serves Range.
  /// The credentials do NOT go in the URL: mpv gets them as a header instead,
  /// so they never land in a log line or on screen.
  Uri fileUrl(String path) => _uri('/api/file', {'path': path});

  Future<Map<String, dynamic>> listFiles(String path) async {
    final res =
        await http.get(_uri('/api/files', {'path': path}), headers: authHeader);
    if (res.statusCode == 401) {
      throw Exception(
        'HTTP 401 — the server wants credentials.\n'
        'Set HOARD_USER and HOARD_PASS in run.sh.',
      );
    }
    if (res.statusCode != 200) {
      throw Exception('GET /api/files -> ${res.statusCode}');
    }
    return jsonDecode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getProgress(String path) async {
    final res = await http.get(_uri('/api/progress', {'path': path}),
        headers: authHeader);
    if (res.statusCode != 200) return {};
    return jsonDecode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
  }

  Future<void> saveProgress(
      String path, double position, double duration) async {
    await http.post(
      _uri('/api/progress', {'path': path}),
      headers: {'Content-Type': 'application/json', ...authHeader},
      body: jsonEncode({
        'position': position,
        'duration': duration,
        'cut_in': null,
        'cut_out': null,
      }),
    );
  }
}

// ── App shell ─────────────────────────────────────────────────────────────────

class SpikeApp extends StatelessWidget {
  const SpikeApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Hoard spike',
        debugShowCheckedModeBanner: false,
        theme: ThemeData.dark(useMaterial3: true).copyWith(
          // Readable at arm's length on the Deck's 1280x800 panel.
          textTheme: ThemeData.dark().textTheme.apply(fontSizeFactor: 1.25),
        ),
        home: const ServerScreen(),
      );
}

// ── Screen 1: server address, with both keyboards side by side ────────────────

class ServerScreen extends StatefulWidget {
  const ServerScreen({super.key});

  @override
  State<ServerScreen> createState() => _ServerScreenState();
}

class _ServerScreenState extends State<ServerScreen> {
  // Pre-filled from the launcher, so that the whole test survives the very
  // failure it is meant to observe: if neither keyboard works in Gaming Mode,
  // the address is already there and everything downstream stays reachable.
  final _controller = TextEditingController(
    text: Platform.environment['HOARD_URL'] ?? 'http://192.168.1.10:8000',
  );
  String _typedWithOwnKeyboard = '';

  @override
  void initState() {
    super.initState();
    // The remembered address only fills in when the launcher says nothing.
    // The other way round, a wrong address saved once would outrank run.sh
    // for good — and with no working keyboard there would be no way back.
    if (Platform.environment['HOARD_URL'] != null) return;
    SharedPreferences.getInstance().then((prefs) {
      final saved = prefs.getString('baseUrl');
      if (saved != null && mounted) {
        setState(() => _controller.text = saved);
      }
    });
  }

  Future<void> _connect(String url) async {
    final clean = url.trim().replaceAll(RegExp(r'/+$'), '');
    if (clean.isEmpty) return;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('baseUrl', clean);
    if (!mounted) return;
    Navigator.of(context).push(MaterialPageRoute(
      builder: (_) => BrowseScreen(api: HoardApi(clean), path: ''),
    ));
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('Hoard — feasibility spike')),
        body: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            // Test A: the ordinary field, served by whatever keyboard the
            // system provides. This is the one expected to misbehave in
            // Gaming Mode — try Steam+X, then the Quick Access Menu.
            Text(
              HoardApi.authConfigured
                  ? 'Credentials: set in run.sh'
                  : 'Credentials: NONE — set HOARD_USER / HOARD_PASS in run.sh '
                      'if the server answers 401',
              style: TextStyle(
                fontSize: 15,
                color: HoardApi.authConfigured ? Colors.green : Colors.orange,
              ),
            ),
            const SizedBox(height: 16),
            const Text('A — system keyboard',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _controller,
              style: const TextStyle(fontSize: 20),
              decoration: const InputDecoration(border: OutlineInputBorder()),
            ),
            const SizedBox(height: 10),
            FilledButton(
              onPressed: () => _connect(_controller.text),
              child: const Text('Connect with this address'),
            ),
            const Divider(height: 36),
            // Test B: same input, served by our own on-screen keyboard. If this
            // works where A does not, the design choice is vindicated.
            const Text('B — built-in keyboard (D-pad)',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(border: Border.all(color: Colors.grey)),
              child: Text(
                _typedWithOwnKeyboard.isEmpty
                    ? '(empty)'
                    : _typedWithOwnKeyboard,
                style: const TextStyle(fontFamily: 'monospace', fontSize: 20),
              ),
            ),
            const SizedBox(height: 10),
            OnScreenKeyboard(
              initialValue: _typedWithOwnKeyboard,
              onChanged: (v) => setState(() => _typedWithOwnKeyboard = v),
              onSubmit: _connect,
            ),
          ],
        ),
      );
}

// ── Built-in on-screen keyboard ───────────────────────────────────────────────

/// Gamepad-driven keyboard. In Gaming Mode, Steam Input maps the pad onto
/// arrow keys and Enter by default, so handling those covers the controller.
class OnScreenKeyboard extends StatefulWidget {
  const OnScreenKeyboard({
    super.key,
    required this.onChanged,
    this.onSubmit,
    this.initialValue = '',
  });

  final ValueChanged<String> onChanged;
  final ValueChanged<String>? onSubmit;
  final String initialValue;

  @override
  State<OnScreenKeyboard> createState() => _OnScreenKeyboardState();
}

class _OnScreenKeyboardState extends State<OnScreenKeyboard> {
  static const _rows = <String>[
    '1234567890',
    'azertyuiop',
    'qsdfghjklm',
    'wxcvbn.:/-',
  ];

  int _row = 0;
  int _col = 0;
  late String _value = widget.initialValue;

  void _emit(String v) {
    setState(() => _value = v);
    widget.onChanged(v);
  }

  KeyEventResult _onKey(FocusNode node, KeyEvent event) {
    if (event is! KeyDownEvent && event is! KeyRepeatEvent) {
      return KeyEventResult.ignored;
    }
    final key = event.logicalKey;
    if (key == LogicalKeyboardKey.arrowRight) {
      setState(() => _col = (_col + 1) % _rows[_row].length);
    } else if (key == LogicalKeyboardKey.arrowLeft) {
      setState(
          () => _col = (_col - 1 + _rows[_row].length) % _rows[_row].length);
    } else if (key == LogicalKeyboardKey.arrowDown) {
      setState(() {
        _row = (_row + 1) % _rows.length;
        _col = _col.clamp(0, _rows[_row].length - 1);
      });
    } else if (key == LogicalKeyboardKey.arrowUp) {
      setState(() {
        _row = (_row - 1 + _rows.length) % _rows.length;
        _col = _col.clamp(0, _rows[_row].length - 1);
      });
    } else if (key == LogicalKeyboardKey.enter) {
      _emit(_value + _rows[_row][_col]);
    } else if (key == LogicalKeyboardKey.backspace) {
      if (_value.isNotEmpty) _emit(_value.substring(0, _value.length - 1));
    } else {
      return KeyEventResult.ignored;
    }
    return KeyEventResult.handled;
  }

  @override
  Widget build(BuildContext context) => Focus(
        onKeyEvent: _onKey,
        child: Builder(
          builder: (context) {
            final focused = Focus.of(context).hasFocus;
            return Column(
              children: [
                for (var r = 0; r < _rows.length; r++)
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      for (var c = 0; c < _rows[r].length; c++)
                        GestureDetector(
                          onTap: () => _emit(_value + _rows[r][c]),
                          child: Container(
                            margin: const EdgeInsets.all(2),
                            width: 46,
                            height: 46,
                            alignment: Alignment.center,
                            decoration: BoxDecoration(
                              color: (r == _row && c == _col && focused)
                                  ? Colors.blue
                                  : Colors.grey.shade800,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(_rows[r][c],
                                style: const TextStyle(fontSize: 18)),
                          ),
                        ),
                    ],
                  ),
                const SizedBox(height: 6),
                Text(
                  focused
                      ? 'D-pad to move · A to type · B to erase'
                      : 'Tap the keyboard to give it focus',
                  style: const TextStyle(fontSize: 13, color: Colors.grey),
                ),
                const SizedBox(height: 8),
                if (widget.onSubmit != null)
                  FilledButton.tonal(
                    onPressed: () => widget.onSubmit!(_value),
                    child: const Text('Connect with what I typed here'),
                  ),
              ],
            );
          },
        ),
      );
}

// ── Screen 2: flat folder listing, D-pad navigable ────────────────────────────

class BrowseScreen extends StatefulWidget {
  const BrowseScreen({super.key, required this.api, required this.path});

  final HoardApi api;
  final String path;

  @override
  State<BrowseScreen> createState() => _BrowseScreenState();
}

class _BrowseScreenState extends State<BrowseScreen> {
  late final Future<Map<String, dynamic>> _future =
      widget.api.listFiles(widget.path);
  final _scroll = ScrollController();
  List<Map<String, dynamic>> _entries = const [];
  int _cursor = 0;

  void _open(Map<String, dynamic> e) {
    final isDir = e['is_dir'] as bool;
    Navigator.of(context).push(MaterialPageRoute(
      builder: (_) => isDir
          ? BrowseScreen(api: widget.api, path: e['path'] as String)
          : PlayerScreen(api: widget.api, path: e['path'] as String),
    ));
  }

  KeyEventResult _onKey(FocusNode node, KeyEvent event) {
    if (_entries.isEmpty) return KeyEventResult.ignored;
    if (event is! KeyDownEvent && event is! KeyRepeatEvent) {
      return KeyEventResult.ignored;
    }
    final key = event.logicalKey;
    if (key == LogicalKeyboardKey.arrowDown) {
      setState(() => _cursor = (_cursor + 1) % _entries.length);
    } else if (key == LogicalKeyboardKey.arrowUp) {
      setState(() => _cursor = (_cursor - 1 + _entries.length) % _entries.length);
    } else if (key == LogicalKeyboardKey.enter) {
      _open(_entries[_cursor]);
      return KeyEventResult.handled;
    } else if (key == LogicalKeyboardKey.escape) {
      if (Navigator.of(context).canPop()) Navigator.of(context).pop();
      return KeyEventResult.handled;
    } else {
      return KeyEventResult.ignored;
    }
    // Keep the cursor on screen: 64px per row is the ListTile height here.
    _scroll.animateTo(
      (_cursor * 64.0 - 200).clamp(0, _scroll.position.maxScrollExtent),
      duration: const Duration(milliseconds: 120),
      curve: Curves.easeOut,
    );
    return KeyEventResult.handled;
  }

  @override
  void dispose() {
    _scroll.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: Text(widget.path.isEmpty ? '/' : widget.path)),
        body: Focus(
          autofocus: true,
          onKeyEvent: _onKey,
          child: FutureBuilder<Map<String, dynamic>>(
            future: _future,
            builder: (context, snap) {
              if (snap.hasError) {
                return Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Text('Error: ${snap.error}',
                        style: const TextStyle(fontSize: 18)),
                  ),
                );
              }
              if (!snap.hasData) {
                return const Center(child: CircularProgressIndicator());
              }
              _entries =
                  (snap.data!['entries'] as List).cast<Map<String, dynamic>>();
              return ListView.builder(
                controller: _scroll,
                itemCount: _entries.length,
                itemBuilder: (context, i) {
                  final e = _entries[i];
                  final isDir = e['is_dir'] as bool;
                  final progress = e['progress'] as Map<String, dynamic>?;
                  final percent = progress?['percent'];
                  return Container(
                    color: i == _cursor
                        ? Colors.blue.withValues(alpha: 0.3)
                        : null,
                    child: ListTile(
                      leading: Icon(isDir ? Icons.folder : Icons.movie),
                      title: Text(e['name'] as String),
                      subtitle: percent == null ? null : Text('$percent %'),
                      onTap: () {
                        setState(() => _cursor = i);
                        _open(e);
                      },
                    ),
                  );
                },
              );
            },
          ),
        ),
      );
}

// ── Screen 3: playback, diagnostics and the decode comparison ─────────────────

class PlayerScreen extends StatefulWidget {
  const PlayerScreen({super.key, required this.api, required this.path});

  final HoardApi api;
  final String path;

  @override
  State<PlayerScreen> createState() => _PlayerScreenState();
}

class _PlayerScreenState extends State<PlayerScreen>
    with SingleTickerProviderStateMixin {
  /// Repaint every frame while playing.
  ///
  /// media_kit does not reliably tell Flutter that a new video frame landed in
  /// the texture, so the picture only advances when the UI happens to repaint
  /// for some other reason. Measured on a Steam Deck: 8 fps at rest, 25 fps as
  /// soon as any animation was on screen — mpv reporting zero dropped frames
  /// throughout, because mpv was never the one falling behind. This ticker
  /// supplies the missing repaints. It is a workaround, not a fix: it keeps
  /// the machine drawing continuously and costs battery.
  Ticker? _repaintTicker;

  late final Player _player = Player();
  late final VideoController _controller = VideoController(_player);
  Timer? _diagnosticsTimer;
  Map<String, String> _diagnostics = {};
  Duration _position = Duration.zero;
  Duration _duration = Duration.zero;

  /// One measured run per decoder mode, keyed by what we asked mpv for.
  final Map<String, _ProbeResult> _results = {};

  /// Off by default so the difference is visible: turn it on and the picture
  /// should go from 8 fps to the source rate, with nothing else changed.
  bool _forceRepaint = false;
  int _flutterFrames = 0;
  String _hwdec = 'auto-safe';
  bool _measuring = false;
  String _measureStep = '';

  @override
  void initState() {
    super.initState();
    // Count frames Flutter actually rendered. This is the grandeur that was
    // missing: mpv's counters describe mpv, and mpv was never the problem.
    SchedulerBinding.instance.addTimingsCallback(_countFrames);
    _start();
  }

  void _countFrames(List<FrameTiming> timings) => _flutterFrames += timings.length;

  /// mpv does its own HTTP, so Dart's Authorization header does not reach it.
  /// Passing the credentials as a header rather than inside the URL keeps them
  /// out of mpv's logs and out of anything shown on screen.
  Media _media() => Media(
        widget.api.fileUrl(widget.path).toString(),
        httpHeaders: HoardApi.authHeader,
      );

  Future<void> _setHwdec(String value) async {
    final platform = _player.platform;
    if (platform is NativePlayer) {
      await platform.setProperty('hwdec', value);
    }
  }

  Future<void> _start() async {
    final progress = await widget.api.getProgress(widget.path);
    final resumeAt = (progress['position'] as num?)?.toDouble() ?? 0;

    _player.stream.position.listen((p) => _position = p);
    _player.stream.duration.listen((d) => _duration = d);

    // Must be set before the file is opened: mpv picks its decoder at load.
    await _setHwdec(_hwdec);
    await _player.open(_media());
    if (resumeAt > 1) {
      await _player.seek(Duration(milliseconds: (resumeAt * 1000).round()));
    }
    // Poll mpv properties rather than reading them once: hwdec-current only
    // settles after the first frames have been decoded.
    _diagnosticsTimer =
        Timer.periodic(const Duration(seconds: 1), (_) => _readDiagnostics());
  }

  void _setForceRepaint(bool on) {
    setState(() {
      _forceRepaint = on;
      if (on) {
        _repaintTicker ??= createTicker((_) => setState(() {}));
        _repaintTicker!.start();
      } else {
        _repaintTicker?.stop();
      }
    });
  }

  Future<String> _prop(String name) async {
    final platform = _player.platform;
    if (platform is! NativePlayer) return '(no native player)';
    try {
      return await platform.getProperty(name);
    } catch (_) {
      return '(unavailable)';
    }
  }

  Future<void> _readDiagnostics() async {
    final values = <String, String>{};
    for (final property in const [
      'hwdec-current',
      'video-codec',
      'video-params/w',
      'video-params/h',
      // container-fps is the SOURCE rate. An earlier build showed
      // estimated-vf-fps and read it as the displayed rate: it says 25 whether
      // you see 25 frames or 8, so it could not describe the problem at all.
      'container-fps',
      'frame-drop-count',
      'decoder-frame-drop-count',
    ]) {
      values[property] = await _prop(property);
    }
    if (mounted) setState(() => _diagnostics = values);
  }

  double _num(String raw) => double.tryParse(raw.trim()) ?? double.nan;

  /// Measure one decoder mode: what mpv settled on, how many frames the
  /// output actually threw away, and what that costs the CPU.
  ///
  /// Dropped frames are the measurement that matters here. The decoder can
  /// keep up perfectly while the display path collapses — that is exactly
  /// what `vaapi-copy` does, bouncing every frame through main memory — and
  /// only the drop counters distinguish the two.
  Future<void> _probe(String mode) async {
    if (_measuring) return;
    final restartAt = _position;
    setState(() {
      _measuring = true;
      _hwdec = mode;
      _measureStep = 'settling';
    });

    await _setHwdec(mode);
    // Reopening is what makes mpv re-pick its decoder.
    await _player.open(_media());
    await _player.seek(restartAt);
    await Future<void>.delayed(const Duration(seconds: 5));

    if (!mounted) return;
    setState(() => _measureStep = 'measuring 15 s');

    final sourceFps = _num(await _prop('container-fps'));
    final dropsBefore = _num(await _prop('frame-drop-count'));
    final decoderDropsBefore = _num(await _prop('decoder-frame-drop-count'));
    final cpuBefore = _cpuSecondsUsed();
    final framesBefore = _flutterFrames;
    final started = DateTime.now();

    await Future<void>.delayed(const Duration(seconds: 15));

    final elapsed = DateTime.now().difference(started).inMicroseconds / 1e6;
    final dropped = _num(await _prop('frame-drop-count')) - dropsBefore;
    final decoderDropped =
        _num(await _prop('decoder-frame-drop-count')) - decoderDropsBefore;
    final cpu = (_cpuSecondsUsed() - cpuBefore) / elapsed * 100;
    final painted = (_flutterFrames - framesBefore) / elapsed;
    final used = await _prop('hwdec-current');

    if (!mounted) return;
    setState(() {
      _results['$mode${_forceRepaint ? " +repaint" : ""}'] = _ProbeResult(
        requested: '$mode${_forceRepaint ? " +repaint" : ""}',
        used: used,
        sourceFps: sourceFps,
        droppedPerSecond: dropped / elapsed,
        decoderDroppedPerSecond: decoderDropped / elapsed,
        cpuPercent: cpu,
        paintedFps: painted,
      );
      _measuring = false;
      _measureStep = '';
    });
  }

  @override
  void dispose() {
    _diagnosticsTimer?.cancel();
    _repaintTicker?.dispose();
    SchedulerBinding.instance.removeTimingsCallback(_countFrames);
    // Save where we stopped, so the web UI picks the file up at the same place.
    if (_duration.inSeconds > 0) {
      widget.api.saveProgress(
        widget.path,
        _position.inMilliseconds / 1000,
        _duration.inMilliseconds / 1000,
      );
    }
    _player.dispose();
    super.dispose();
  }

  static const _modes = <String, String>{
    'vaapi': 'vaapi (no copy)',
    'auto-safe': 'auto-safe',
    'no': 'software',
  };

  Widget _verdict() {
    if (_measuring) {
      return Card(
        color: Colors.blue.shade900,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              const SizedBox(
                  width: 22, height: 22, child: CircularProgressIndicator()),
              const SizedBox(width: 14),
              Expanded(
                child: Text('$_hwdec — $_measureStep\n'
                    '20 s. Leave it playing.'),
              ),
            ],
          ),
        ),
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        SwitchListTile(
          contentPadding: EdgeInsets.zero,
          dense: true,
          value: _forceRepaint,
          onChanged: _setForceRepaint,
          title: const Text('Force a repaint every frame',
              style: TextStyle(fontSize: 15)),
          subtitle: const Text(
            'Flip it while the video plays and watch the Steam counter',
            style: TextStyle(fontSize: 12),
          ),
        ),
        const Text('Measure each decoder (20 s per run)',
            style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        for (final entry in _modes.entries)
          Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: FilledButton.tonal(
              onPressed: () => _probe(entry.key),
              child: Text(entry.value),
            ),
          ),
        const SizedBox(height: 8),
        for (final r in _results.values) _resultCard(r),
      ],
    );
  }

  Widget _resultCard(_ProbeResult r) {
    // Smooth now means Flutter PAINTED at the source rate. Dropped frames were
    // the wrong signal: mpv reported zero while the picture crawled at 8 fps,
    // because mpv was filling a texture nobody was repainting.
    final smooth = r.paintedFps.isFinite && r.paintedFps >= r.sourceFps - 2;
    return Card(
      color: smooth ? Colors.green.shade900 : Colors.orange.shade900,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '${r.requested} -> ${r.used}${smooth ? "  SMOOTH" : "  DROPPING"}',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 6),
            for (final line in [
              'source        ${r.sourceFps.toStringAsFixed(0)} fps',
              'PAINTED       ${r.paintedFps.toStringAsFixed(1)} fps  <- what you see',
              'mpv dropped   ${r.droppedPerSecond.toStringAsFixed(1)} /s'
                  '  (decoder ${r.decoderDroppedPerSecond.toStringAsFixed(1)})',
              'CPU           ${r.cpuPercent.toStringAsFixed(0)} % of one core',
            ])
              Text(line,
                  style:
                      const TextStyle(fontFamily: 'monospace', fontSize: 14)),
          ],
        ),
      ),
    );
  }

  Widget _readouts() => ListView(
        padding: const EdgeInsets.all(12),
        children: [
          _verdict(),
          const SizedBox(height: 12),
          Text('hwdec requested  $_hwdec',
              style: const TextStyle(fontFamily: 'monospace', fontSize: 15)),
          if (_diagnostics.isEmpty)
            const Text('(waiting for the first frames…)')
          else
            for (final entry in _diagnostics.entries)
              Text(
                '${entry.key.padRight(18)} ${entry.value}',
                style: const TextStyle(fontFamily: 'monospace', fontSize: 15),
              ),
        ],
      );

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: Text(widget.path.split('/').last)),
        // Side by side in landscape. A full-width 16:9 video on the Deck's
        // 1280x800 panel is 720px tall and pushes every reading off-screen —
        // which is the one thing this screen exists to show.
        body: LayoutBuilder(
          builder: (context, box) {
            final video = AspectRatio(
              aspectRatio: 16 / 9,
              child: Video(controller: _controller),
            );
            if (box.maxWidth < box.maxHeight) {
              return Column(
                children: [video, Expanded(child: _readouts())],
              );
            }
            return Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(width: box.maxWidth * 0.55, child: video),
                Expanded(child: _readouts()),
              ],
            );
          },
        ),
      );
}

/// One measured run of the player under a given decoder mode.
class _ProbeResult {
  const _ProbeResult({
    required this.requested,
    required this.used,
    required this.sourceFps,
    required this.droppedPerSecond,
    required this.decoderDroppedPerSecond,
    required this.cpuPercent,
    required this.paintedFps,
  });

  /// What we asked mpv for, which is not always what it settled on.
  final String requested;
  final String used;
  final double sourceFps;

  /// Frames the video output threw away, per second. This is the number that
  /// describes a stuttering picture; a healthy decoder with a collapsing
  /// display path shows up here and nowhere else.
  final double droppedPerSecond;
  final double decoderDroppedPerSecond;
  final double cpuPercent;

  /// Frames Flutter actually rendered per second — the displayed rate, which
  /// mpv's own counters cannot see.
  final double paintedFps;
}
