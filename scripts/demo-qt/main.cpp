// Qt6 Widgets gallery for checking the Slate Kvantum theme. It mirrors scripts/demo-gtk4.py 1:1:
// same window size, grid, captions, widget order and content text, so whole windows compare pixel for pixel.
// Every widget has a stable objectName (the gallery id); --bounds writes window-relative device-pixel rects.
// Notes: Qt has no switch (a QCheckBox stands in), no segmented control (a QTabBar), no infobar (a QFrame),
// no expander (a QToolButton plus a QLabel). The theme is chosen by the caller (QT_STYLE_OVERRIDE=kvantum).
// --mode only names the window; SLATE_QT_FONT=1 (set by scripts/qt-env.sh) forces Inter 9.75pt (13px at 96 dpi).
#include <QApplication>
#include <QCalendarWidget>
#include <QCheckBox>
#include <QComboBox>
#include <QDate>
#include <QFile>
#include <QFrame>
#include <QGridLayout>
#include <QHBoxLayout>
#include <QHeaderView>
#include <QIcon>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLabel>
#include <QLineEdit>
#include <QListWidget>
#include <QMainWindow>
#include <QMap>
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
#include <QToolButton>
#include <QToolTip>
#include <QTreeWidget>
#include <QVBoxLayout>

static const QMap<QString, QString> NAMES = {
    {"button", "Button"}, {"button-suggested", "Suggested button"}, {"button-destructive", "Destructive button"},
    {"button-flat", "Flat button"}, {"segmented", "Segmented control"}, {"entry", "Text field"},
    {"search", "Search field"}, {"spin", "Spin button"}, {"dropdown", "Dropdown"}, {"check", "Checkbox"},
    {"radio", "Radio button"}, {"switch", "Switch"}, {"slider", "Slider"}, {"progress", "Progress bar"},
    {"levelbar", "Level bar"}, {"scrollbar", "Scrollbar"}, {"tooltip", "Tooltip"}, {"popover", "Popover"},
    {"dialog", "Dialog"}, {"tabs", "Tabs"}, {"infobar", "Info bar"}, {"list", "List"}, {"sidebar", "Sidebar"},
    {"tree", "Table"}, {"calendar", "Calendar"}, {"expander", "Expander"},
};

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
    const bool pinned = qEnvironmentVariableIsSet("SLATE_QT_FONT");
    if (pinned) {
        QFont f("Inter"); f.setPointSizeF(9.75); app.setFont(f);
        QIcon::setThemeName("Adwaita");
    }
    fprintf(stderr, "style: %s mode: %s\n", qPrintable(app.style()->objectName()), qPrintable(mode));

    auto themed = [](const char *name) { return QIcon::fromTheme(name); };

    QMainWindow win;
    win.setWindowTitle("Slate gallery - " + mode);
    QMap<QString, QWidget *> ids;

    // header bar: back/forward left, title centered, search and menu right
    auto *tb = new QToolBar;
    tb->setMovable(false);
    auto tool = [&](const char *icon) { auto *b = new QToolButton; b->setIcon(themed(icon)); b->setAutoRaise(false); return b; };
    tb->addWidget(tool("go-previous-symbolic"));
    tb->addWidget(tool("go-next-symbolic"));
    auto spacer = [] { auto *s = new QWidget; s->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred); return s; };
    tb->addWidget(spacer());
    tb->addWidget(new QLabel("Slate"));
    tb->addWidget(spacer());
    tb->addWidget(tool("system-search-symbolic"));
    auto *menuBtn = tool("open-menu-symbolic");
    tb->addWidget(menuBtn);
    win.addToolBar(tb);
    tb->setObjectName("titlebar-toolbar");
    ids["titlebar-toolbar"] = tb;

    auto *central = new QWidget;
    auto *g = new QGridLayout(central);
    g->setContentsMargins(16, 16, 16, 16);
    g->setHorizontalSpacing(12);
    g->setVerticalSpacing(14);
    tb->setFixedHeight(40); // GTK header bar height
    // GTK columns are homogeneous: force four equal columns, whatever a widget's minimum size asks for
    for (int c = 0; c < 4; ++c) { g->setColumnStretch(c, 1); g->setColumnMinimumWidth(c, (w - 32 - 3 * 12) / 4); }

    // cell: a small caption over the widget; natural widgets keep their width (left-aligned), the rest fill the cell
    auto cell = [&](QWidget *wd, const char *id, int r, int c, int rs = 1, int cs = 1, const char *label = nullptr,
                    bool natural = false, bool register_id = true) {
        wd->setObjectName(id);
        if (register_id) ids[id] = wd;
        auto *box = new QWidget;
        auto *v = new QVBoxLayout(box);
        v->setContentsMargins(0, 0, 0, 0);
        v->setSpacing(4);
        auto *cap = new QLabel(NAMES.value(label ? label : id, label ? label : id));
        QFont cf = cap->font(); if (pinned) cf.setPointSizeF(8.25); cap->setFont(cf);
        QPalette pal = cap->palette(); pal.setColor(QPalette::WindowText, pal.color(QPalette::PlaceholderText)); cap->setPalette(pal);
        v->addWidget(cap);
        wd->setSizePolicy(wd->sizePolicy().horizontalPolicy(), QSizePolicy::Fixed);
        v->addWidget(wd, 0, natural ? Qt::AlignLeft : Qt::Alignment());
        v->addStretch(1);
        g->addWidget(box, r, c, rs, cs);
    };
    auto row = [&](std::initializer_list<QWidget *> ws) {
        auto *c = new QWidget; auto *l = new QHBoxLayout(c);
        l->setContentsMargins(0, 0, 0, 0); l->setSpacing(12);
        for (auto *x : ws) l->addWidget(x);
        l->addStretch(1);
        return c;
    };

    cell(new QPushButton("Button"), "button", 0, 0, 1, 1, nullptr, true);
    auto *sug = new QPushButton("Suggested"); sug->setDefault(true);
    cell(sug, "button-suggested", 0, 1, 1, 1, nullptr, true);
    auto *des = new QPushButton("Destructive"); des->setProperty("destructive", true); // no Kvantum equivalent
    cell(des, "button-destructive", 0, 2, 1, 1, nullptr, true);
    auto *flat = new QPushButton("Flat"); flat->setFlat(true);
    cell(flat, "button-flat", 0, 3, 1, 1, nullptr, true);

    auto *seg = new QTabBar; seg->setExpanding(false); seg->setDrawBase(false);
    for (auto t : {"Day", "Week", "Month"}) seg->addTab(t);
    cell(seg, "segmented", 1, 0, 1, 1, nullptr, true);
    cell(new QLineEdit("Text entry"), "entry", 1, 1);
    auto *search = new QLineEdit("slate"); search->setClearButtonEnabled(true);
    search->addAction(themed("edit-find-symbolic"), QLineEdit::LeadingPosition);
    cell(search, "search", 1, 2);
    auto *spin = new QSpinBox; spin->setRange(0, 100); spin->setValue(42);
    cell(spin, "spin", 1, 3, 1, 1, nullptr, true);

    auto *dd = new QComboBox; dd->addItems({"Dropdown", "Second", "Third"});
    cell(dd, "dropdown", 2, 0, 1, 1, nullptr, true);
    auto *on = new QCheckBox("On"); on->setChecked(true);
    cell(row({on, new QCheckBox("Off")}), "check", 2, 1);
    auto *ron = new QRadioButton("On"); ron->setChecked(true);
    cell(row({ron, new QRadioButton("Off")}), "radio", 2, 2);
    auto *swOn = new QCheckBox; swOn->setChecked(true); // stand-in: Qt has no switch
    cell(row({swOn, new QCheckBox}), "switch", 2, 3);

    auto *sl = new QSlider(Qt::Horizontal); sl->setRange(0, 100); sl->setValue(40);
    cell(sl, "slider", 3, 0, 1, 2);
    auto *pr = new QProgressBar; pr->setRange(0, 100); pr->setValue(60); pr->setTextVisible(false);
    cell(pr, "progress", 3, 2);
    auto *lv = new QProgressBar; lv->setRange(0, 100); lv->setValue(70); lv->setTextVisible(false);
    cell(lv, "levelbar", 3, 3);

    // GTK adjustment: value 20, 0..100, page 40, so Qt's maximum is 100 - 40
    auto *sb = new QScrollBar(Qt::Horizontal); sb->setRange(0, 60); sb->setPageStep(40); sb->setValue(20);
    cell(sb, "scrollbar", 4, 0);
    auto *tip = new QPushButton("Hover me"); tip->setToolTip("A tooltip in Slate");
    cell(tip, "tooltip", 4, 1, 1, 1, nullptr, true);
    auto *popBtn = new QPushButton("Open popover");
    cell(popBtn, "popover-button", 4, 2, 1, 1, "popover", true, false);
    auto *dlgBtn = new QPushButton("Show dialog");
    cell(dlgBtn, "dialog-button", 4, 3, 1, 1, "dialog", true, false);

    auto *tabs = new QTabWidget;
    for (auto t : {"General", "Appearance", "Advanced"}) {
        auto *l = new QLabel(QString("%1 settings").arg(t)); l->setAlignment(Qt::AlignCenter); l->setContentsMargins(0, 12, 0, 12);
        tabs->addTab(l, t);
    }
    cell(tabs, "tabs", 5, 0, 1, 2);

    auto *info = new QFrame; info->setFrameShape(QFrame::StyledPanel);
    auto *il = new QHBoxLayout(info);
    il->addWidget(new QLabel("A new Slate build is ready."), 1);
    il->addWidget(new QPushButton("Update"));
    auto *close = new QToolButton; close->setIcon(themed("window-close-symbolic")); il->addWidget(close);
    cell(info, "infobar", 5, 2, 1, 2);

    auto *list = new QListWidget; list->addItems({"Inbox", "Drafts", "Sent"}); list->setCurrentRow(1);
    list->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff); list->setVerticalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    list->setFixedHeight(3 * list->sizeHintForRow(0) + 2 * list->frameWidth());
    cell(list, "list", 6, 0);

    auto *side = new QListWidget; side->addItems({"Library", "Recent", "Starred"}); side->setCurrentRow(0);
    side->setFixedHeight(105);
    cell(side, "sidebar", 6, 1);

    auto *tree = new QTreeWidget; tree->setHeaderLabels({"Name", "Kind", "Size"});
    tree->setRootIsDecorated(false);
    for (auto r : {QStringList{"slate.css", "CSS", "12 KB"}, QStringList{"tokens.json", "JSON", "4 KB"}, QStringList{"build.py", "Python", "9 KB"}})
        new QTreeWidgetItem(tree, r);
    tree->setCurrentItem(tree->topLevelItem(1));
    tree->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff); tree->setVerticalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    tree->setFixedHeight(tree->header()->sizeHint().height() + 3 * tree->sizeHintForRow(0) + 2 * tree->frameWidth());
    cell(tree, "tree", 6, 2);

    auto *cal = new QCalendarWidget;
    cal->setVerticalHeaderFormat(QCalendarWidget::NoVerticalHeader); cal->setGridVisible(false);
    cal->setFirstDayOfWeek(Qt::Sunday);
    cal->setSelectedDate(QDate::currentDate());
    cal->setMinimumWidth(1); // let the cell width win over the calendar's own minimum, like GTK4's homogeneous column
    cell(cal, "calendar", 6, 3, 2, 1);

    auto *exp = new QWidget; auto *el = new QVBoxLayout(exp);
    el->setContentsMargins(0, 0, 0, 0); el->setSpacing(0);
    auto *eb = new QToolButton; eb->setArrowType(Qt::DownArrow); eb->setText("Expander");
    eb->setToolButtonStyle(Qt::ToolButtonTextBesideIcon); eb->setAutoRaise(true);
    el->addWidget(eb, 0, Qt::AlignLeft);
    auto *ed = new QLabel("Hidden details appear here.\nSecond line of the content."); ed->setContentsMargins(16, 4, 0, 0);
    el->addWidget(ed);
    cell(exp, "expander", 7, 0, 1, 3);

    g->setRowStretch(8, 1);
    win.setCentralWidget(central);
    win.resize(w, h);
    win.show();
    win.activateWindow(); // Xvfb has no window manager: without this Qt paints the inactive (backdrop) palette, GTK4 does not

    QMenu *menu = nullptr; QMessageBox *dlg = nullptr; QFrame *pop = nullptr;
    auto showDialog = [&] {
        dlg = new QMessageBox(QMessageBox::NoIcon, "Dialog", "Discard changes?", QMessageBox::NoButton, &win);
        dlg->setObjectName("dialog"); dlg->setInformativeText("Unsaved edits will be lost.");
        dlg->addButton("Cancel", QMessageBox::RejectRole); dlg->addButton("Discard", QMessageBox::AcceptRole);
        dlg->setModal(false); dlg->show();
        dlg->move(win.mapToGlobal(QPoint((w - dlg->width()) / 2, (h - dlg->height()) / 2)));
    };
    QObject::connect(dlgBtn, &QPushButton::clicked, &app, showDialog);
    QTimer::singleShot(500, &app, [&] {
        if (show == "menu") {
            menu = new QMenu(&win); menu->setObjectName("menu");
            for (auto t : {"New Window", "Open…", "Save As…"}) menu->addAction(t);
            menu->addSeparator();
            for (auto t : {"Preferences", "Keyboard Shortcuts"}) menu->addAction(t);
            menu->addSeparator(); menu->addAction("About Slate");
            menu->popup(menuBtn->mapToGlobal(QPoint(menuBtn->width() - menu->sizeHint().width(), menuBtn->height())));
        } else if (show == "popover") {
            pop = new QFrame(&win, Qt::Popup); pop->setObjectName("popover"); pop->setFrameShape(QFrame::StyledPanel);
            auto *pv = new QVBoxLayout(pop); pv->setContentsMargins(12, 12, 12, 12); pv->setSpacing(8);
            auto *hd = new QLabel("Notifications"); QFont bf = hd->font(); bf.setWeight(QFont::DemiBold); hd->setFont(bf);
            pv->addWidget(hd);
            auto *pr2 = new QHBoxLayout; pr2->addWidget(new QLabel("Do not disturb"), 1);
            auto *ps = new QCheckBox; ps->setChecked(true); pr2->addWidget(ps); pv->addLayout(pr2);
            auto *snooze = new QLineEdit; snooze->setPlaceholderText("Snooze for…"); pv->addWidget(snooze);
            pop->adjustSize();
            pop->move(popBtn->mapToGlobal(QPoint((popBtn->width() - pop->width()) / 2, popBtn->height() + 4)));
            pop->show();
        } else if (show == "tooltip") {
            QToolTip::showText(tip->mapToGlobal(QPoint(0, tip->height() + 4)), tip->toolTip(), nullptr, QRect(), 600000);
        } else if (show == "dialog") {
            showDialog();
        }
    });
    QTimer::singleShot(1200, &app, [&] {
        if (boundsFile.isEmpty()) return;
        const qreal d = win.devicePixelRatioF();
        auto arr = [&](QRect r) { return QJsonArray{int(r.x() * d), int(r.y() * d), int(r.width() * d), int(r.height() * d)}; };
        QJsonObject o;
        o["window"] = arr(win.geometry());
        for (auto it = ids.begin(); it != ids.end(); ++it)
            o[it.key()] = arr(QRect(it.value()->mapTo(&win, QPoint(0, 0)), it.value()->size()));
        const QPoint origin = win.geometry().topLeft();
        auto popup = [&](QWidget *p, const char *n) { if (p) o[n] = arr(QRect(p->geometry().topLeft() - origin, p->size())); };
        popup(menu, "menu"); popup(dlg, "dialog"); popup(pop, "popover");
        if (show == "tooltip")
            for (auto *t : QApplication::topLevelWidgets()) if (t->inherits("QTipLabel") && t->isVisible()) popup(t, "tooltip-tip");
        QFile f(boundsFile);
        if (f.open(QIODevice::WriteOnly)) f.write(QJsonDocument(o).toJson());
        fprintf(stderr, "bounds: %d keys\n", int(o.size()));
    });
    if (quitAfter) QTimer::singleShot(quitAfter, &app, &QApplication::quit);
    return app.exec();
}
