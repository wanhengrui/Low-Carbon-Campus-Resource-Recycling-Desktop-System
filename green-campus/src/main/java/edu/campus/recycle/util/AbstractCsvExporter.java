package edu.campus.recycle.util;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

/**
 * CSV 导出模板方法（模板方法模式，契约第 8 节）。
 *
 * <p>固定流程：建目录 → 写 UTF-8 BOM → 表头 → 数据行 → 关闭资源；
 * 子类只负责组装表头与数据行，消除"打开文件/编码/资源释放"的重复代码。</p>
 */
public abstract class AbstractCsvExporter {

    /** UTF-8 BOM，保证 Excel 直接双击打开不乱码 */
    private static final String UTF8_BOM = "\uFEFF";

    /**
     * 导出模板方法（final：流程不可被覆写）。
     *
     * @param target 目标文件
     * @param header 表头
     * @param rows   数据行
     * @return 目标文件路径的字符串形式
     * @throws IOException 写文件失败
     */
    public final String export(Path target, List<String> header, List<List<String>> rows) throws IOException {
        if (target == null) {
            throw new IllegalArgumentException("导出目标路径不能为空");
        }
        Path absolute = target.toAbsolutePath();
        if (absolute.getParent() != null) {
            Files.createDirectories(absolute.getParent());
        }
        try (Writer writer = new BufferedWriter(new OutputStreamWriter(
                Files.newOutputStream(absolute), StandardCharsets.UTF_8))) {
            writer.write(UTF8_BOM);
            writeLine(writer, header);
            if (rows != null) {
                for (List<String> row : rows) {
                    writeLine(writer, row);
                }
            }
            writer.flush();
        }
        return absolute.toString();
    }

    /**
     * 钩子：导出内容描述（子类可覆写用于日志）。
     *
     * @return 描述
     */
    protected String describe() {
        return "CSV";
    }

    private void writeLine(Writer writer, List<String> values) throws IOException {
        if (values == null) {
            writer.write("\r\n");
            return;
        }
        StringBuilder line = new StringBuilder();
        for (int i = 0; i < values.size(); i++) {
            if (i > 0) {
                line.append(',');
            }
            line.append(escape(values.get(i)));
        }
        writer.write(line.toString());
        writer.write("\r\n");
    }

    private String escape(String value) {
        if (value == null) {
            return "";
        }
        boolean needQuote = value.indexOf(',') >= 0 || value.indexOf('"') >= 0
                || value.indexOf('\n') >= 0 || value.indexOf('\r') >= 0;
        if (!needQuote) {
            return value;
        }
        return '"' + value.replace("\"", "\"\"") + '"';
    }
}
