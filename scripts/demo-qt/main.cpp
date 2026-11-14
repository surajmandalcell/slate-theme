// Qt6 Widgets gallery for checking the Slate Kvantum theme.
// Every widget has a stable objectName; --bounds writes window-relative device-pixel rects.
// Notes: Qt has no switch (a QCheckBox stands in) and no KMessageWidget (a QFrame stands in).
// The theme is chosen by the caller (QT_STYLE_OVERRIDE=kvantum + Kvantum config); --mode only names the window.
#include <QApplication>
#include <QCalendarWidget>
#include <QCheckBox>
#include <QComboBox>
#include <QFile>
#include <QFrame>
#include <QGridLayout>
#include <QHBoxLayout>
#include <QHeaderView>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLabel>
#include <QLineEdit>
#include <QListWidget>
#include <QMainWindow>
#include <QMenu>
#include <QMessageBox>
#include <QProgressBar>
#include <QPushButton>
#include <QRadioButton>
#include <QScrollBar>
#include <QSlider>
#include <QSpinBox>
#include <QStyle>
#include <QTabBar>
#include <QTabWidget>
#include <QTimer>
#include <QToolBar>
#include <QToolBox>
#include <QToolButton>
#include <QToolTip>
#include <QTreeWidget>

static QWidget *named(QWidget *w, const char *name) { w->setObjectName(name); return w; }

int main(int argc, char **argv) {
    QApplication app(argc, argv);
    QString mode = "light", boundsFile, show;
    int w = 1100, h = 760, quitAfter = 0;
    const QStringList a = app.arguments();
    for (int i = 1; i + 1 < a.size(); ++i) {
        if (a[i] == "--mode") mode = a[i + 1];
        else if (a[i] == "--bounds") boundsFile = a[i + 1];
        else if (a[i] == "--show") show = a[i + 1];
        else if (a[i] == "--quit-after") quitAfter = a[i + 1].toInt();
        else if (a[i] == "--size") { auto p = a[i + 1].split('x'); if (p.size() == 2) { w = p[0].toInt(); h = p[1].toInt(); } }
    }
    fprintf(stderr, "style: %s mode: %s\n", qPrintable(app.style()->objectName()), qPrintable(mode));

    QStyle *st = app.style();
    auto icon = [&](QStyle::StandardPixmap p) { return st->standardIcon(p); };

    QMainWindow win;
    win.setWindowTitle("Slate gallery - " + mode);
    auto *tb = new QToolBar;
    tb->setMovable(false);
    for (auto p : {QStyle::SP_ArrowBack, QStyle::SP_ArrowForward, QStyle::SP_BrowserReload}) {
        auto *b = new QToolButton; b->setIcon(icon(p)); b->setAutoRaise(true); tb->addWidget(b);
    }
    tb->addSeparator();
    tb->addWidget(new QLabel(" Title "));
    win.addToolBar(tb);
    named(tb, "titlebar-toolbar");

    auto *central = new QWidget;
    auto *g = new QGridLayout(central);
    auto cell = [&](QWidget *wd, const char *n, int r, int c, int rs = 1, int cs = 1, bool natural = false) {
        named(wd, n);
        g->addWidget(wd, r, c, rs, cs, natural ? Qt::AlignLeft | Qt::AlignVCenter : Qt::Alignment());
    };

    cell(new QPushButton("Button"), "button", 0, 0, 1, 1, true);
    auto *sug = new QPushButton("Suggested"); sug->setDefault(true);
    cell(sug, "button-suggested", 0, 1, 1, 1, true);
    auto *des = new QPushButton("Destructive"); des->setProperty("destructive", true); // no Kvantum equivalent
    cell(des, "button-destructive", 0, 2, 1, 1, true);
    auto *flat = new QPushButton("Flat"); flat->setFlat(true);
    cell(flat, "button-flat", 0, 3, 1, 1, true);

    auto *seg = new QTabBar; seg->setExpanding(false); seg->setDrawBase(false);
    for (auto t : {"Day", "Week", "Month"}) seg->addTab(t);
    cell(seg, "segmented", 1, 0, 1, 1, true);
    auto *entry = new QLineEdit("Text entry"); cell(entry, "entry", 1, 1);
    auto *search = new QLineEdit; search->setPlaceholderText("Search"); search->setClearButtonEnabled(true);
    search->setText("query");
    search->addAction(QIcon::fromTheme("edit-find", icon(QStyle::SP_FileDialogContentsView)), QLineEdit::LeadingPosition);
    cell(search, "search", 1, 2);
    auto *spin = new QSpinBox; spin->setValue(42); cell(spin, "spin", 1, 3);

    auto *dd = new QComboBox; dd->addItems({"Dropdown", "Second", "Third"}); cell(dd, "dropdown", 2, 0);
    auto *chk = new QCheckBox("Check"); chk->setChecked(true); cell(chk, "check", 2, 1, 1, 1, true);
    auto *rad = new QRadioButton("Radio"); rad->setChecked(true); cell(rad, "radio", 2, 2, 1, 1, true);
    auto *sw = new QCheckBox("Switch (checkbox)"); sw->setChecked(true); cell(sw, "switch", 2, 3, 1, 1, true);

    auto *sl = new QSlider(Qt::Horizontal); sl->setValue(40); cell(sl, "slider", 3, 0);
    auto *pr = new QProgressBar; pr->setValue(60); cell(pr, "progress", 3, 1);
    auto *lv = new QProgressBar; lv->setValue(35); lv->setTextVisible(false); cell(lv, "levelbar", 3, 2);
    auto *sb = new QScrollBar(Qt::Horizontal); sb->setRange(0, 100); sb->setPageStep(30); sb->setValue(20);
    cell(sb, "scrollbar", 3, 3);

    auto *tabs = new QTabWidget;
    for (auto t : {"General", "Advanced", "About"}) tabs->addTab(new QLabel(QString("%1 page").arg(t)), t);
    cell(tabs, "tabs", 4, 0, 1, 2);
    auto *list = new QListWidget; list->addItems({"List row 1", "List row 2", "List row 3", "List row 4"});
    list->setCurrentRow(1); cell(list, "list", 4, 2);
    auto *side = new QListWidget;
    const std::pair<const char *, QStyle::StandardPixmap> sideRows[] = {
        {"Home", QStyle::SP_DirHomeIcon}, {"Documents", QStyle::SP_FileIcon}, {"Downloads", QStyle::SP_ArrowDown}, {"Trash", QStyle::SP_TrashIcon}};
    for (auto &r : sideRows) side->addItem(new QListWidgetItem(icon(r.second), r.first));
    side->setCurrentRow(0); cell(side, "sidebar", 4, 3);

    auto *tree = new QTreeWidget; tree->setHeaderLabels({"Name", "Size", "Kind"});
    for (int i = 0; i < 3; ++i) {
        auto *it = new QTreeWidgetItem(tree, {QString("Item %1").arg(i + 1), QString::number((i + 1) * 12), "Folder"});
        new QTreeWidgetItem(it, {"Child", "3", "File"});
    }
    tree->expandAll(); tree->setCurrentItem(tree->topLevelItem(1)); cell(tree, "tree", 5, 0, 1, 2);
    auto *tbox = new QToolBox;
    for (auto t : {"Section one", "Section two", "Section three"}) tbox->addItem(new QLabel(QString("%1 content").arg(t)), t);
    cell(tbox, "expander", 5, 2);
    cell(new QCalendarWidget, "calendar", 5, 3);

    auto *info = new QFrame; info->setFrameShape(QFrame::StyledPanel);
    auto *il = new QHBoxLayout(info); il->addWidget(new QLabel("Info bar: something worth knowing (QFrame stand-in for KMessageWidget)"));
    cell(info, "infobar", 6, 0, 1, 4);

    g->setRowStretch(4, 1); g->setRowStretch(5, 2);
    win.setCentralWidget(central);
    win.resize(w, h);
    win.show();

    QMenu *menu = nullptr; QMessageBox *dlg = nullptr;
    QTimer::singleShot(500, &app, [&] {
        const QPoint at = win.mapToGlobal(QPoint(w - 330, 80));
        if (show == "menu") {
            menu = new QMenu(&win); named(menu, "menu");
            menu->addAction("Open"); auto *c = menu->addAction("Checkable"); c->setCheckable(true); c->setChecked(true);
            menu->addSeparator(); menu->addAction(icon(QStyle::SP_DialogSaveButton), "Save");
            menu->addMenu("Submenu")->addAction("Inner");
            menu->addAction("Disabled")->setEnabled(false);
            menu->popup(at);
        } else if (show == "tooltip") {
            QToolTip::showText(at, "Tooltip text", nullptr, QRect(), 600000);
        } else if (show == "dialog") {
            dlg = new QMessageBox(QMessageBox::Question, "Dialog", "Discard changes?", QMessageBox::Yes | QMessageBox::No, &win);
            named(dlg, "dialog"); dlg->setInformativeText("This cannot be undone."); dlg->setModal(false); dlg->show();
            dlg->move(win.mapToGlobal(QPoint((w - dlg->width()) / 2, (h - dlg->height()) / 2)));
        }
    });
    QTimer::singleShot(1200, &app, [&] {
        if (boundsFile.isEmpty()) return;
        const qreal d = win.devicePixelRatioF();
        auto arr = [&](QRect r) { return QJsonArray{int(r.x() * d), int(r.y() * d), int(r.width() * d), int(r.height() * d)}; };
        QJsonObject o;
        o["window"] = arr(win.geometry());
        for (auto *wd : central->findChildren<QWidget *>(QString(), Qt::FindDirectChildrenOnly))
            if (!wd->objectName().isEmpty()) o[wd->objectName()] = arr(QRect(wd->mapTo(&win, QPoint(0, 0)), wd->size()));
        o["titlebar-toolbar"] = arr(QRect(tb->mapTo(&win, QPoint(0, 0)), tb->size()));
        const QPoint origin = win.geometry().topLeft();
        auto popup = [&](QWidget *p, const char *n) { if (p) o[n] = arr(QRect(p->geometry().topLeft() - origin, p->size())); };
        popup(menu, "menu"); popup(dlg, "dialog");
        if (show == "tooltip")
            for (auto *t : QApplication::topLevelWidgets()) if (t->inherits("QTipLabel") && t->isVisible()) popup(t, "tooltip");
        QFile f(boundsFile);
        if (f.open(QIODevice::WriteOnly)) f.write(QJsonDocument(o).toJson());
        fprintf(stderr, "bounds: %d keys\n", int(o.size()));
    });
    if (quitAfter) QTimer::singleShot(quitAfter, &app, &QApplication::quit);
    return app.exec();
}
