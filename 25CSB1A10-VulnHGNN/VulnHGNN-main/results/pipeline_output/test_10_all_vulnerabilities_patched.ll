; ModuleID = 'test_files\test_10_all_vulnerabilities.c'
source_filename = "test_files\\test_10_all_vulnerabilities.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.51.36252"

$sprintf = comdat any

$vsprintf = comdat any

$_snprintf = comdat any

$_vsnprintf = comdat any

$printf = comdat any

$_vsprintf_l = comdat any

$_vsnprintf_l = comdat any

$__local_stdio_printf_options = comdat any

$_vfprintf_l = comdat any

$"??_C@_0BI@BOCLKCFJ@V1?3?5?$CFd?0?5V2?3?5?$CFd?0?5V3?3?5?$CFd?6?$AA@" = comdat any

@"??_C@_0BI@BOCLKCFJ@V1?3?5?$CFd?0?5V2?3?5?$CFd?0?5V3?3?5?$CFd?6?$AA@" = linkonce_odr dso_local unnamed_addr constant [24 x i8] c"V1: %d, V2: %d, V3: %d\0A\00", comdat, align 8, !dbg !0
@__local_stdio_printf_options._OptionsStorage = internal global i64 0, align 8, !dbg !7

; Function Attrs: noinline nounwind uwtable
define linkonce_odr dso_local i32 @sprintf(ptr noundef %0, ptr noundef %1, ...) #0 comdat !dbg !29 {
  %3 = alloca ptr, align 8
  %4 = alloca ptr, align 8
  %5 = alloca i32, align 4
  %6 = alloca ptr, align 8
  store ptr %1, ptr %3, align 8
    #dbg_declare(ptr %3, !39, !DIExpression(), !40)
  store ptr %0, ptr %4, align 8
    #dbg_declare(ptr %4, !41, !DIExpression(), !42)
    #dbg_declare(ptr %5, !43, !DIExpression(), !44)
    #dbg_declare(ptr %6, !45, !DIExpression(), !48)
  call void @llvm.va_start.p0(ptr %6), !dbg !49
  %7 = load ptr, ptr %6, align 8, !dbg !50
  %8 = load ptr, ptr %3, align 8, !dbg !50
  %9 = load ptr, ptr %4, align 8, !dbg !50
  %10 = call i32 @_vsprintf_l(ptr noundef %9, ptr noundef %8, ptr noundef null, ptr noundef %7), !dbg !50
  store i32 %10, ptr %5, align 4, !dbg !50
  call void @llvm.va_end.p0(ptr %6), !dbg !51
  %11 = load i32, ptr %5, align 4, !dbg !52
  ret i32 %11, !dbg !52
}

; Function Attrs: noinline nounwind uwtable
define linkonce_odr dso_local i32 @vsprintf(ptr noundef %0, ptr noundef %1, ptr noundef %2) #0 comdat !dbg !53 {
  %4 = alloca ptr, align 8
  %5 = alloca ptr, align 8
  %6 = alloca ptr, align 8
  store ptr %2, ptr %4, align 8
    #dbg_declare(ptr %4, !56, !DIExpression(), !57)
  store ptr %1, ptr %5, align 8
    #dbg_declare(ptr %5, !58, !DIExpression(), !59)
  store ptr %0, ptr %6, align 8
    #dbg_declare(ptr %6, !60, !DIExpression(), !61)
  %7 = load ptr, ptr %4, align 8, !dbg !62
  %8 = load ptr, ptr %5, align 8, !dbg !62
  %9 = load ptr, ptr %6, align 8, !dbg !62
  %10 = call i32 @_vsnprintf_l(ptr noundef %9, i64 noundef -1, ptr noundef %8, ptr noundef null, ptr noundef %7), !dbg !62
  ret i32 %10, !dbg !62
}

; Function Attrs: noinline nounwind uwtable
define linkonce_odr dso_local i32 @_snprintf(ptr noundef %0, i64 noundef %1, ptr noundef %2, ...) #0 comdat !dbg !63 {
  %4 = alloca ptr, align 8
  %5 = alloca i64, align 8
  %6 = alloca ptr, align 8
  %7 = alloca i32, align 4
  %8 = alloca ptr, align 8
  store ptr %2, ptr %4, align 8
    #dbg_declare(ptr %4, !67, !DIExpression(), !68)
  store i64 %1, ptr %5, align 8
    #dbg_declare(ptr %5, !69, !DIExpression(), !70)
  store ptr %0, ptr %6, align 8
    #dbg_declare(ptr %6, !71, !DIExpression(), !72)
    #dbg_declare(ptr %7, !73, !DIExpression(), !74)
    #dbg_declare(ptr %8, !75, !DIExpression(), !76)
  call void @llvm.va_start.p0(ptr %8), !dbg !77
  %9 = load ptr, ptr %8, align 8, !dbg !78
  %10 = load ptr, ptr %4, align 8, !dbg !78
  %11 = load i64, ptr %5, align 8, !dbg !78
  %12 = load ptr, ptr %6, align 8, !dbg !78
  %13 = call i32 @_vsnprintf(ptr noundef %12, i64 noundef %11, ptr noundef %10, ptr noundef %9), !dbg !78
  store i32 %13, ptr %7, align 4, !dbg !78
  call void @llvm.va_end.p0(ptr %8), !dbg !79
  %14 = load i32, ptr %7, align 4, !dbg !80
  ret i32 %14, !dbg !80
}

; Function Attrs: noinline nounwind uwtable
define linkonce_odr dso_local i32 @_vsnprintf(ptr noundef %0, i64 noundef %1, ptr noundef %2, ptr noundef %3) #0 comdat !dbg !81 {
  %5 = alloca ptr, align 8
  %6 = alloca ptr, align 8
  %7 = alloca i64, align 8
  %8 = alloca ptr, align 8
  store ptr %3, ptr %5, align 8
    #dbg_declare(ptr %5, !84, !DIExpression(), !85)
  store ptr %2, ptr %6, align 8
    #dbg_declare(ptr %6, !86, !DIExpression(), !87)
  store i64 %1, ptr %7, align 8
    #dbg_declare(ptr %7, !88, !DIExpression(), !89)
  store ptr %0, ptr %8, align 8
    #dbg_declare(ptr %8, !90, !DIExpression(), !91)
  %9 = load ptr, ptr %5, align 8, !dbg !92
  %10 = load ptr, ptr %6, align 8, !dbg !92
  %11 = load i64, ptr %7, align 8, !dbg !92
  %12 = load ptr, ptr %8, align 8, !dbg !92
  %13 = call i32 @_vsnprintf_l(ptr noundef %12, i64 noundef %11, ptr noundef %10, ptr noundef null, ptr noundef %9), !dbg !92
  ret i32 %13, !dbg !92
}

; Function Attrs: noinline nounwind uwtable
define dso_local void @the_ultimate_test(i32 noundef %0, i32 noundef %1, i32 noundef %2) #0 !dbg !93 {
  %4 = alloca i32, align 4
  %5 = alloca i32, align 4
  %6 = alloca i32, align 4
  %7 = alloca ptr, align 8
  %8 = alloca i32, align 4
  %9 = alloca i32, align 4
  %10 = alloca i32, align 4
  store i32 %2, ptr %4, align 4
    #dbg_declare(ptr %4, !96, !DIExpression(), !97)
  store i32 %1, ptr %5, align 4
    #dbg_declare(ptr %5, !98, !DIExpression(), !97)
  store i32 %0, ptr %6, align 4
    #dbg_declare(ptr %6, !99, !DIExpression(), !97)
    #dbg_declare(ptr %7, !100, !DIExpression(), !101)
  %11 = call noalias ptr @malloc(i64 noundef 4) #4, !dbg !101, !heapallocsite !18
  store ptr %11, ptr %7, align 8, !dbg !101
  %12 = load i32, ptr %6, align 4, !dbg !102
  %13 = load ptr, ptr %7, align 8, !dbg !102
  store i32 %12, ptr %13, align 4, !dbg !102
    #dbg_declare(ptr %8, !103, !DIExpression(), !104)
  %14 = load ptr, ptr %7, align 8, !dbg !104
  %15 = load i32, ptr %14, align 4, !dbg !104
  %16 = add i32 %15, 2147483647, !dbg !104
  store i32 %16, ptr %8, align 4, !dbg !104
    #dbg_declare(ptr %9, !105, !DIExpression(), !106)
  %17 = load i32, ptr %5, align 4, !dbg !106
  %18 = sub i32 %17, 2000000, !dbg !106
  store i32 %18, ptr %9, align 4, !dbg !106
    #dbg_declare(ptr %10, !107, !DIExpression(), !108)
  %19 = load i32, ptr %8, align 4, !dbg !108
  %20 = load i32, ptr %4, align 4, !dbg !108
  %21 = sdiv i32 %19, %20, !dbg !108
  store i32 %21, ptr %10, align 4, !dbg !108
  %22 = load i32, ptr %10, align 4, !dbg !109
  %23 = load i32, ptr %9, align 4, !dbg !109
  %24 = load i32, ptr %8, align 4, !dbg !109
  %25 = call i32 (ptr, ...) @printf(ptr noundef @"??_C@_0BI@BOCLKCFJ@V1?3?5?$CFd?0?5V2?3?5?$CFd?0?5V3?3?5?$CFd?6?$AA@", i32 noundef %24, i32 noundef %23, i32 noundef %22), !dbg !109
  %26 = load ptr, ptr %7, align 8, !dbg !110
  call void @free(ptr noundef %26), !dbg !110
  ret void, !dbg !111
}

; Function Attrs: allocsize(0)
declare dso_local noalias ptr @malloc(i64 noundef) #1

; Function Attrs: noinline nounwind uwtable
define linkonce_odr dso_local i32 @printf(ptr noundef %0, ...) #0 comdat !dbg !112 {
  %2 = alloca ptr, align 8
  %3 = alloca i32, align 4
  %4 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
    #dbg_declare(ptr %2, !115, !DIExpression(), !116)
    #dbg_declare(ptr %3, !117, !DIExpression(), !118)
    #dbg_declare(ptr %4, !119, !DIExpression(), !120)
  call void @llvm.va_start.p0(ptr %4), !dbg !121
  %5 = load ptr, ptr %4, align 8, !dbg !122
  %6 = load ptr, ptr %2, align 8, !dbg !122
  %7 = call ptr @__acrt_iob_func(i32 noundef 1), !dbg !122
  %8 = call i32 @_vfprintf_l(ptr noundef %7, ptr noundef %6, ptr noundef null, ptr noundef %5), !dbg !122
  store i32 %8, ptr %3, align 4, !dbg !122
  call void @llvm.va_end.p0(ptr %4), !dbg !123
  %9 = load i32, ptr %3, align 4, !dbg !124
  ret i32 %9, !dbg !124
}

declare dso_local void @free(ptr noundef) #2

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @main() #0 !dbg !125 {
  %1 = alloca i32, align 4
  store i32 0, ptr %1, align 4
  call void @the_ultimate_test(i32 noundef 100, i32 noundef -2147483548, i32 noundef 0), !dbg !128
  ret i32 0, !dbg !129
}

; Function Attrs: nocallback nofree nosync nounwind willreturn
declare void @llvm.va_start.p0(ptr) #3

; Function Attrs: noinline nounwind uwtable
define linkonce_odr dso_local i32 @_vsprintf_l(ptr noundef %0, ptr noundef %1, ptr noundef %2, ptr noundef %3) #0 comdat !dbg !130 {
  %5 = alloca ptr, align 8
  %6 = alloca ptr, align 8
  %7 = alloca ptr, align 8
  %8 = alloca ptr, align 8
  store ptr %3, ptr %5, align 8
    #dbg_declare(ptr %5, !146, !DIExpression(), !147)
  store ptr %2, ptr %6, align 8
    #dbg_declare(ptr %6, !148, !DIExpression(), !149)
  store ptr %1, ptr %7, align 8
    #dbg_declare(ptr %7, !150, !DIExpression(), !151)
  store ptr %0, ptr %8, align 8
    #dbg_declare(ptr %8, !152, !DIExpression(), !153)
  %9 = load ptr, ptr %5, align 8, !dbg !154
  %10 = load ptr, ptr %6, align 8, !dbg !154
  %11 = load ptr, ptr %7, align 8, !dbg !154
  %12 = load ptr, ptr %8, align 8, !dbg !154
  %13 = call i32 @_vsnprintf_l(ptr noundef %12, i64 noundef -1, ptr noundef %11, ptr noundef %10, ptr noundef %9), !dbg !154
  ret i32 %13, !dbg !154
}

; Function Attrs: nocallback nofree nosync nounwind willreturn
declare void @llvm.va_end.p0(ptr) #3

; Function Attrs: noinline nounwind uwtable
define linkonce_odr dso_local i32 @_vsnprintf_l(ptr noundef %0, i64 noundef %1, ptr noundef %2, ptr noundef %3, ptr noundef %4) #0 comdat !dbg !155 {
  %6 = alloca ptr, align 8
  %7 = alloca ptr, align 8
  %8 = alloca ptr, align 8
  %9 = alloca i64, align 8
  %10 = alloca ptr, align 8
  %11 = alloca i32, align 4
  store ptr %4, ptr %6, align 8
    #dbg_declare(ptr %6, !158, !DIExpression(), !159)
  store ptr %3, ptr %7, align 8
    #dbg_declare(ptr %7, !160, !DIExpression(), !161)
  store ptr %2, ptr %8, align 8
    #dbg_declare(ptr %8, !162, !DIExpression(), !163)
  store i64 %1, ptr %9, align 8
    #dbg_declare(ptr %9, !164, !DIExpression(), !165)
  store ptr %0, ptr %10, align 8
    #dbg_declare(ptr %10, !166, !DIExpression(), !167)
    #dbg_declare(ptr %11, !168, !DIExpression(), !170)
  %12 = load ptr, ptr %6, align 8, !dbg !170
  %13 = load ptr, ptr %7, align 8, !dbg !170
  %14 = load ptr, ptr %8, align 8, !dbg !170
  %15 = load i64, ptr %9, align 8, !dbg !170
  %16 = load ptr, ptr %10, align 8, !dbg !170
  %17 = call ptr @__local_stdio_printf_options(), !dbg !170
  %18 = load i64, ptr %17, align 8, !dbg !170
  %19 = or i64 %18, 1, !dbg !170
  %20 = call i32 @__stdio_common_vsprintf(i64 noundef %19, ptr noundef %16, i64 noundef %15, ptr noundef %14, ptr noundef %13, ptr noundef %12), !dbg !170
  store i32 %20, ptr %11, align 4, !dbg !170
  %21 = load i32, ptr %11, align 4, !dbg !171
  %22 = icmp slt i32 %21, 0, !dbg !171
  br i1 %22, label %23, label %24, !dbg !171

23:                                               ; preds = %5
  br label %26, !dbg !171

24:                                               ; preds = %5
  %25 = load i32, ptr %11, align 4, !dbg !171
  br label %26, !dbg !171

26:                                               ; preds = %24, %23
  %27 = phi i32 [ -1, %23 ], [ %25, %24 ], !dbg !171
  ret i32 %27, !dbg !171
}

declare dso_local i32 @__stdio_common_vsprintf(i64 noundef, ptr noundef, i64 noundef, ptr noundef, ptr noundef, ptr noundef) #2

; Function Attrs: noinline nounwind uwtable
define linkonce_odr dso_local ptr @__local_stdio_printf_options() #0 comdat !dbg !9 {
  ret ptr @__local_stdio_printf_options._OptionsStorage, !dbg !172
}

; Function Attrs: noinline nounwind uwtable
define linkonce_odr dso_local i32 @_vfprintf_l(ptr noundef %0, ptr noundef %1, ptr noundef %2, ptr noundef %3) #0 comdat !dbg !173 {
  %5 = alloca ptr, align 8
  %6 = alloca ptr, align 8
  %7 = alloca ptr, align 8
  %8 = alloca ptr, align 8
  store ptr %3, ptr %5, align 8
    #dbg_declare(ptr %5, !184, !DIExpression(), !185)
  store ptr %2, ptr %6, align 8
    #dbg_declare(ptr %6, !186, !DIExpression(), !187)
  store ptr %1, ptr %7, align 8
    #dbg_declare(ptr %7, !188, !DIExpression(), !189)
  store ptr %0, ptr %8, align 8
    #dbg_declare(ptr %8, !190, !DIExpression(), !191)
  %9 = load ptr, ptr %5, align 8, !dbg !192
  %10 = load ptr, ptr %6, align 8, !dbg !192
  %11 = load ptr, ptr %7, align 8, !dbg !192
  %12 = load ptr, ptr %8, align 8, !dbg !192
  %13 = call ptr @__local_stdio_printf_options(), !dbg !192
  %14 = load i64, ptr %13, align 8, !dbg !192
  %15 = call i32 @__stdio_common_vfprintf(i64 noundef %14, ptr noundef %12, ptr noundef %11, ptr noundef %10, ptr noundef %9), !dbg !192
  ret i32 %15, !dbg !192
}

declare dso_local ptr @__acrt_iob_func(i32 noundef) #2

declare dso_local i32 @__stdio_common_vfprintf(i64 noundef, ptr noundef, ptr noundef, ptr noundef, ptr noundef) #2

attributes #0 = { noinline nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { allocsize(0) "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #2 = { "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { nocallback nofree nosync nounwind willreturn }
attributes #4 = { allocsize(0) }

!llvm.dbg.cu = !{!15}
!llvm.module.flags = !{!23, !24, !25, !26, !27}
!llvm.ident = !{!28}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(scope: null, file: !2, line: 24, type: !3, isLocal: true, isDefinition: true)
!2 = !DIFile(filename: "test_files\\test_10_all_vulnerabilities.c", directory: "C:\\Users\\saida\\Sai_Dattu\\Sai_Dattu\\NIT W\\3rd Sem\\TOACD\\Screenrecordings and Code\\VulnHGNN-Vulnerbility and selfhealing\\VulnHGNN-main", checksumkind: CSK_MD5, checksum: "28619f83f18f3fa5ac8e7ab617589736")
!3 = !DICompositeType(tag: DW_TAG_array_type, baseType: !4, size: 192, elements: !5)
!4 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!5 = !{!6}
!6 = !DISubrange(count: 24)
!7 = !DIGlobalVariableExpression(var: !8, expr: !DIExpression())
!8 = distinct !DIGlobalVariable(name: "_OptionsStorage", scope: !9, file: !10, line: 91, type: !14, isLocal: true, isDefinition: true)
!9 = distinct !DISubprogram(name: "__local_stdio_printf_options", scope: !10, file: !10, line: 89, type: !11, scopeLine: 90, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !15, retainedNodes: !22)
!10 = !DIFile(filename: "C:\\Program Files (x86)\\Windows Kits\\10\\Include\\10.0.26100.0\\ucrt\\corecrt_stdio_config.h", directory: "", checksumkind: CSK_MD5, checksum: "dacf907bda504afb0b64f53a242bdae6")
!11 = !DISubroutineType(types: !12)
!12 = !{!13}
!13 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !14, size: 64)
!14 = !DIBasicType(name: "unsigned long long", size: 64, encoding: DW_ATE_unsigned)
!15 = distinct !DICompileUnit(language: DW_LANG_C11, file: !2, producer: "clang version 23.1.2 (https://github.com/llvm/llvm-project 85ac560262434c9ccfc0c183ec22d4138ed647fb)", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, retainedTypes: !16, globals: !21, splitDebugInlining: false, nameTableKind: None)
!16 = !{!17, !19}
!17 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !18, size: 64)
!18 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!19 = !DIDerivedType(tag: DW_TAG_typedef, name: "size_t", file: !20, line: 188, baseType: !14)
!20 = !DIFile(filename: "C:\\Program Files (x86)\\Microsoft Visual Studio\\18\\BuildTools\\VC\\Tools\\MSVC\\14.51.36231\\include\\vcruntime.h", directory: "", checksumkind: CSK_MD5, checksum: "c2fc75a6044a5fbbc118f5d0881e74d8")
!21 = !{!0}
!22 = !{!7}
!23 = !{i32 2, !"CodeView", i32 1}
!24 = !{i32 2, !"Debug Info Version", i32 3}
!25 = !{i32 8, !"PIC Level", i32 2}
!26 = !{i32 7, !"uwtable", i32 2}
!27 = !{i32 1, !"MaxTLSAlign", i32 65536}
!28 = !{!"clang version 23.1.2 (https://github.com/llvm/llvm-project 85ac560262434c9ccfc0c183ec22d4138ed647fb)"}
!29 = distinct !DISubprogram(name: "sprintf", scope: !30, file: !30, line: 1764, type: !31, scopeLine: 1771, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !15, retainedNodes: !38)
!30 = !DIFile(filename: "C:\\Program Files (x86)\\Windows Kits\\10\\Include\\10.0.26100.0\\ucrt\\stdio.h", directory: "", checksumkind: CSK_MD5, checksum: "c1a1fbc43e7d45f0ea4ae539ddcffb19")
!31 = !DISubroutineType(types: !32)
!32 = !{!18, !33, !35, null}
!33 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !34)
!34 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !4, size: 64)
!35 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !36)
!36 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !37, size: 64)
!37 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !4)
!38 = !{}
!39 = !DILocalVariable(name: "_Format", arg: 2, scope: !29, file: !30, line: 1766, type: !35)
!40 = !DILocation(line: 1766, scope: !29)
!41 = !DILocalVariable(name: "_Buffer", arg: 1, scope: !29, file: !30, line: 1765, type: !33)
!42 = !DILocation(line: 1765, scope: !29)
!43 = !DILocalVariable(name: "_Result", scope: !29, file: !30, line: 1772, type: !18)
!44 = !DILocation(line: 1772, scope: !29)
!45 = !DILocalVariable(name: "_ArgList", scope: !29, file: !30, line: 1773, type: !46)
!46 = !DIDerivedType(tag: DW_TAG_typedef, name: "va_list", file: !47, line: 76, baseType: !34)
!47 = !DIFile(filename: "C:\\Program Files (x86)\\Microsoft Visual Studio\\18\\BuildTools\\VC\\Tools\\MSVC\\14.51.36231\\include\\vadefs.h", directory: "", checksumkind: CSK_MD5, checksum: "82edca140cbac673d043e7605ae9bfe1")
!48 = !DILocation(line: 1773, scope: !29)
!49 = !DILocation(line: 1774, scope: !29)
!50 = !DILocation(line: 1776, scope: !29)
!51 = !DILocation(line: 1778, scope: !29)
!52 = !DILocation(line: 1779, scope: !29)
!53 = distinct !DISubprogram(name: "vsprintf", scope: !30, file: !30, line: 1465, type: !54, scopeLine: 1473, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !15, retainedNodes: !38)
!54 = !DISubroutineType(types: !55)
!55 = !{!18, !33, !35, !46}
!56 = !DILocalVariable(name: "_ArgList", arg: 3, scope: !53, file: !30, line: 1468, type: !46)
!57 = !DILocation(line: 1468, scope: !53)
!58 = !DILocalVariable(name: "_Format", arg: 2, scope: !53, file: !30, line: 1467, type: !35)
!59 = !DILocation(line: 1467, scope: !53)
!60 = !DILocalVariable(name: "_Buffer", arg: 1, scope: !53, file: !30, line: 1466, type: !33)
!61 = !DILocation(line: 1466, scope: !53)
!62 = !DILocation(line: 1474, scope: !53)
!63 = distinct !DISubprogram(name: "_snprintf", scope: !30, file: !30, line: 1939, type: !64, scopeLine: 1947, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !15, retainedNodes: !38)
!64 = !DISubroutineType(types: !65)
!65 = !{!18, !33, !66, !35, null}
!66 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !19)
!67 = !DILocalVariable(name: "_Format", arg: 3, scope: !63, file: !30, line: 1942, type: !35)
!68 = !DILocation(line: 1942, scope: !63)
!69 = !DILocalVariable(name: "_BufferCount", arg: 2, scope: !63, file: !30, line: 1941, type: !66)
!70 = !DILocation(line: 1941, scope: !63)
!71 = !DILocalVariable(name: "_Buffer", arg: 1, scope: !63, file: !30, line: 1940, type: !33)
!72 = !DILocation(line: 1940, scope: !63)
!73 = !DILocalVariable(name: "_Result", scope: !63, file: !30, line: 1948, type: !18)
!74 = !DILocation(line: 1948, scope: !63)
!75 = !DILocalVariable(name: "_ArgList", scope: !63, file: !30, line: 1949, type: !46)
!76 = !DILocation(line: 1949, scope: !63)
!77 = !DILocation(line: 1950, scope: !63)
!78 = !DILocation(line: 1951, scope: !63)
!79 = !DILocation(line: 1952, scope: !63)
!80 = !DILocation(line: 1953, scope: !63)
!81 = distinct !DISubprogram(name: "_vsnprintf", scope: !30, file: !30, line: 1402, type: !82, scopeLine: 1411, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !15, retainedNodes: !38)
!82 = !DISubroutineType(types: !83)
!83 = !{!18, !33, !66, !35, !46}
!84 = !DILocalVariable(name: "_ArgList", arg: 4, scope: !81, file: !30, line: 1406, type: !46)
!85 = !DILocation(line: 1406, scope: !81)
!86 = !DILocalVariable(name: "_Format", arg: 3, scope: !81, file: !30, line: 1405, type: !35)
!87 = !DILocation(line: 1405, scope: !81)
!88 = !DILocalVariable(name: "_BufferCount", arg: 2, scope: !81, file: !30, line: 1404, type: !66)
!89 = !DILocation(line: 1404, scope: !81)
!90 = !DILocalVariable(name: "_Buffer", arg: 1, scope: !81, file: !30, line: 1403, type: !33)
!91 = !DILocation(line: 1403, scope: !81)
!92 = !DILocation(line: 1412, scope: !81)
!93 = distinct !DISubprogram(name: "the_ultimate_test", scope: !2, file: !2, line: 9, type: !94, scopeLine: 9, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !15, retainedNodes: !38)
!94 = !DISubroutineType(types: !95)
!95 = !{null, !18, !18, !18}
!96 = !DILocalVariable(name: "c", arg: 3, scope: !93, file: !2, line: 9, type: !18)
!97 = !DILocation(line: 9, scope: !93)
!98 = !DILocalVariable(name: "b", arg: 2, scope: !93, file: !2, line: 9, type: !18)
!99 = !DILocalVariable(name: "a", arg: 1, scope: !93, file: !2, line: 9, type: !18)
!100 = !DILocalVariable(name: "p", scope: !93, file: !2, line: 10, type: !17)
!101 = !DILocation(line: 10, scope: !93)
!102 = !DILocation(line: 13, scope: !93)
!103 = !DILocalVariable(name: "v1", scope: !93, file: !2, line: 16, type: !18)
!104 = !DILocation(line: 16, scope: !93)
!105 = !DILocalVariable(name: "v2", scope: !93, file: !2, line: 19, type: !18)
!106 = !DILocation(line: 19, scope: !93)
!107 = !DILocalVariable(name: "v3", scope: !93, file: !2, line: 22, type: !18)
!108 = !DILocation(line: 22, scope: !93)
!109 = !DILocation(line: 24, scope: !93)
!110 = !DILocation(line: 25, scope: !93)
!111 = !DILocation(line: 26, scope: !93)
!112 = distinct !DISubprogram(name: "printf", scope: !30, file: !30, line: 950, type: !113, scopeLine: 956, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !15, retainedNodes: !38)
!113 = !DISubroutineType(types: !114)
!114 = !{!18, !35, null}
!115 = !DILocalVariable(name: "_Format", arg: 1, scope: !112, file: !30, line: 951, type: !35)
!116 = !DILocation(line: 951, scope: !112)
!117 = !DILocalVariable(name: "_Result", scope: !112, file: !30, line: 957, type: !18)
!118 = !DILocation(line: 957, scope: !112)
!119 = !DILocalVariable(name: "_ArgList", scope: !112, file: !30, line: 958, type: !46)
!120 = !DILocation(line: 958, scope: !112)
!121 = !DILocation(line: 959, scope: !112)
!122 = !DILocation(line: 960, scope: !112)
!123 = !DILocation(line: 961, scope: !112)
!124 = !DILocation(line: 962, scope: !112)
!125 = distinct !DISubprogram(name: "main", scope: !2, file: !2, line: 28, type: !126, scopeLine: 28, spFlags: DISPFlagDefinition, unit: !15)
!126 = !DISubroutineType(types: !127)
!127 = !{!18}
!128 = !DILocation(line: 29, scope: !125)
!129 = !DILocation(line: 30, scope: !125)
!130 = distinct !DISubprogram(name: "_vsprintf_l", scope: !30, file: !30, line: 1449, type: !131, scopeLine: 1458, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !15, retainedNodes: !38)
!131 = !DISubroutineType(types: !132)
!132 = !{!18, !33, !35, !133, !46}
!133 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !134)
!134 = !DIDerivedType(tag: DW_TAG_typedef, name: "_locale_t", file: !135, line: 623, baseType: !136)
!135 = !DIFile(filename: "C:\\Program Files (x86)\\Windows Kits\\10\\Include\\10.0.26100.0\\ucrt\\corecrt.h", directory: "", checksumkind: CSK_MD5, checksum: "93b3a419bcf351413b7b408357260994")
!136 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !137, size: 64)
!137 = !DIDerivedType(tag: DW_TAG_typedef, name: "__crt_locale_pointers", file: !135, line: 621, baseType: !138)
!138 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "__crt_locale_pointers", file: !135, line: 617, size: 128, align: 64, elements: !139)
!139 = !{!140, !143}
!140 = !DIDerivedType(tag: DW_TAG_member, name: "locinfo", scope: !138, file: !135, line: 619, baseType: !141, size: 64)
!141 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !142, size: 64)
!142 = !DICompositeType(tag: DW_TAG_structure_type, name: "__crt_locale_data", file: !135, line: 619, flags: DIFlagFwdDecl)
!143 = !DIDerivedType(tag: DW_TAG_member, name: "mbcinfo", scope: !138, file: !135, line: 620, baseType: !144, size: 64, offset: 64)
!144 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !145, size: 64)
!145 = !DICompositeType(tag: DW_TAG_structure_type, name: "__crt_multibyte_data", file: !135, line: 620, flags: DIFlagFwdDecl)
!146 = !DILocalVariable(name: "_ArgList", arg: 4, scope: !130, file: !30, line: 1453, type: !46)
!147 = !DILocation(line: 1453, scope: !130)
!148 = !DILocalVariable(name: "_Locale", arg: 3, scope: !130, file: !30, line: 1452, type: !133)
!149 = !DILocation(line: 1452, scope: !130)
!150 = !DILocalVariable(name: "_Format", arg: 2, scope: !130, file: !30, line: 1451, type: !35)
!151 = !DILocation(line: 1451, scope: !130)
!152 = !DILocalVariable(name: "_Buffer", arg: 1, scope: !130, file: !30, line: 1450, type: !33)
!153 = !DILocation(line: 1450, scope: !130)
!154 = !DILocation(line: 1459, scope: !130)
!155 = distinct !DISubprogram(name: "_vsnprintf_l", scope: !30, file: !30, line: 1381, type: !156, scopeLine: 1391, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !15, retainedNodes: !38)
!156 = !DISubroutineType(types: !157)
!157 = !{!18, !33, !66, !35, !133, !46}
!158 = !DILocalVariable(name: "_ArgList", arg: 5, scope: !155, file: !30, line: 1386, type: !46)
!159 = !DILocation(line: 1386, scope: !155)
!160 = !DILocalVariable(name: "_Locale", arg: 4, scope: !155, file: !30, line: 1385, type: !133)
!161 = !DILocation(line: 1385, scope: !155)
!162 = !DILocalVariable(name: "_Format", arg: 3, scope: !155, file: !30, line: 1384, type: !35)
!163 = !DILocation(line: 1384, scope: !155)
!164 = !DILocalVariable(name: "_BufferCount", arg: 2, scope: !155, file: !30, line: 1383, type: !66)
!165 = !DILocation(line: 1383, scope: !155)
!166 = !DILocalVariable(name: "_Buffer", arg: 1, scope: !155, file: !30, line: 1382, type: !33)
!167 = !DILocation(line: 1382, scope: !155)
!168 = !DILocalVariable(name: "_Result", scope: !155, file: !30, line: 1392, type: !169)
!169 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !18)
!170 = !DILocation(line: 1392, scope: !155)
!171 = !DILocation(line: 1396, scope: !155)
!172 = !DILocation(line: 92, scope: !9)
!173 = distinct !DISubprogram(name: "_vfprintf_l", scope: !30, file: !30, line: 635, type: !174, scopeLine: 644, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !15, retainedNodes: !38)
!174 = !DISubroutineType(types: !175)
!175 = !{!18, !176, !35, !133, !46}
!176 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !177)
!177 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !178, size: 64)
!178 = !DIDerivedType(tag: DW_TAG_typedef, name: "FILE", file: !179, line: 31, baseType: !180)
!179 = !DIFile(filename: "C:\\Program Files (x86)\\Windows Kits\\10\\Include\\10.0.26100.0\\ucrt\\corecrt_wstdio.h", directory: "", checksumkind: CSK_MD5, checksum: "bf50373b435d0afd0235dd3e05c4a277")
!180 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "_iobuf", file: !179, line: 28, size: 64, align: 64, elements: !181)
!181 = !{!182}
!182 = !DIDerivedType(tag: DW_TAG_member, name: "_Placeholder", scope: !180, file: !179, line: 30, baseType: !183, size: 64)
!183 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 64)
!184 = !DILocalVariable(name: "_ArgList", arg: 4, scope: !173, file: !30, line: 639, type: !46)
!185 = !DILocation(line: 639, scope: !173)
!186 = !DILocalVariable(name: "_Locale", arg: 3, scope: !173, file: !30, line: 638, type: !133)
!187 = !DILocation(line: 638, scope: !173)
!188 = !DILocalVariable(name: "_Format", arg: 2, scope: !173, file: !30, line: 637, type: !35)
!189 = !DILocation(line: 637, scope: !173)
!190 = !DILocalVariable(name: "_Stream", arg: 1, scope: !173, file: !30, line: 636, type: !176)
!191 = !DILocation(line: 636, scope: !173)
!192 = !DILocation(line: 645, scope: !173)
