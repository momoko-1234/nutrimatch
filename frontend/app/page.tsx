"use client";

import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import { analyzeNutritionRisk } from "@/lib/api";
import {
  CHRONIC_CONDITIONS,
  DHC_PRODUCTS,
  DIET_HABITS,
  HEALTH_GOALS,
  ROUTINES,
  SPECIAL_GROUPS,
  SYMPTOM_TAGS
} from "@/lib/constants";
import type {
  AnalyzeResponse,
  BasicProfile,
  ChronicCondition,
  DietHabit,
  HealthGoal,
  Routine,
  SpecialGroup,
  SupplementUse,
  SymptomTag
} from "@/lib/types";

type Screen = "questionnaire" | "supplements" | "results";

const defaultProfile: BasicProfile = {
  age: 32,
  sex: "female",
  height_cm: 165,
  weight_kg: 58,
  routine: "late_sleep",
  diet_habits: ["eating_out"],
  exercise_frequency_per_week: 2,
  water_liters_per_day: 1.5
};

const steps = ["Basic profile", "Special groups", "Symptoms & lifestyle", "Health goals"];

export default function Home() {
  const [screen, setScreen] = useState<Screen>("questionnaire");
  const [step, setStep] = useState(0);
  const [profile, setProfile] = useState<BasicProfile>(defaultProfile);
  const [specialGroups, setSpecialGroups] = useState<SpecialGroup[]>(["metabolic_risk"]);
  const [symptomTags, setSymptomTags] = useState<SymptomTag[]>([
    "high_stress",
    "frequent_late_nights"
  ]);
  const [chronicConditions, setChronicConditions] = useState<ChronicCondition[]>([]);
  const [healthGoals, setHealthGoals] = useState<HealthGoal[]>(["energy", "sleep", "immunity"]);
  const [supplements, setSupplements] = useState<SupplementUse[]>([]);
  const [productSearch, setProductSearch] = useState("");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [useOllama, setUseOllama] = useState(false);

  const filteredProducts = useMemo(() => {
    const query = productSearch.trim().toLowerCase();
    if (!query) return DHC_PRODUCTS;
    return DHC_PRODUCTS.filter((product) =>
      [product.name, product.category, ...product.nutrients, ...product.functions]
        .join(" ")
        .toLowerCase()
        .includes(query)
    );
  }, [productSearch]);

  async function handleAnalyze() {
    setIsLoading(true);
    setError(null);

    try {
      const analysis = await analyzeNutritionRisk({
        profile,
        special_groups: specialGroups,
        symptom_tags: symptomTags,
        chronic_conditions: specialGroups.includes("chronic_patient") ? chronicConditions : [],
        health_goals: healthGoals,
        current_supplements: supplements,
        use_ollama: useOllama
      });
      setResult(analysis);
      setScreen("results");
    } catch (currentError) {
      setError(currentError instanceof Error ? currentError.message : "Analyze failed.");
    } finally {
      setIsLoading(false);
    }
  }

  function toggleArrayValue<T extends string>(
    value: T,
    values: T[],
    setter: (next: T[]) => void
  ) {
    setter(values.includes(value) ? values.filter((item) => item !== value) : [...values, value]);
  }

  function toggleDietHabit(value: DietHabit) {
    setProfile((current) => ({
      ...current,
      diet_habits: current.diet_habits.includes(value)
        ? current.diet_habits.filter((item) => item !== value)
        : [...current.diet_habits, value]
    }));
  }

  function toggleSupplement(productId: string) {
    setSupplements((current) =>
      current.some((item) => item.product_id === productId)
        ? current.filter((item) => item.product_id !== productId)
        : [...current, { product_id: productId }]
    );
  }

  return (
    <main className="min-h-screen bg-[#f5f8f4] text-ink">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-5 py-6 lg:px-8">
        <Hero result={result} />
        <ProcessStrip />

        <div className="flex flex-wrap items-center justify-between gap-3 border-y border-slate-200 py-4">
          <nav className="flex flex-wrap gap-2">
            <TopButton active={screen === "questionnaire"} onClick={() => setScreen("questionnaire")}>
              Questionnaire
            </TopButton>
            <TopButton active={screen === "results"} disabled={!result} onClick={() => setScreen("results")}>
              Results
            </TopButton>
            <TopButton active={screen === "supplements"} onClick={() => setScreen("supplements")}>
              Supplement manager
            </TopButton>
          </nav>
          <button
            className="h-11 rounded-md bg-leaf px-5 font-semibold text-white shadow-sm transition hover:bg-emerald-800 disabled:bg-slate-400"
            disabled={isLoading}
            onClick={handleAnalyze}
            type="button"
          >
            {isLoading ? (useOllama ? "本地模型分析中，首次載入可能需約 2 分鐘…" : "Analyzing") : "Generate advice"}
          </button>
        </div>

        <div className="rounded-md border border-emerald-200 bg-white p-4">
          <label className="flex items-center gap-3 font-semibold">
            <input type="checkbox" checked={useOllama} disabled={isLoading} onChange={(event) => setUseOllama(event.target.checked)} />
            使用本地 Ollama 分析
          </label>
          <p className="mt-2 text-sm text-slate-600">將問卷與規則分析結果交由後端設定的 Ollama 模型產生繁體中文解讀；預設連線至本機，不使用 ChatGPT API。模型無法使用時仍會顯示基本報告。</p>
        </div>
        {screen === "results" && result?.localAI && result.localAI.status !== "disabled" ? (
          <section aria-live="polite" className="rounded-md border border-emerald-200 bg-white p-6">
            <h2 className="text-xl font-bold">本地 AI 營養解讀 · {result.localAI.model}</h2>
            <p className="mt-2 text-sm text-slate-500">{result.localAI.status === "success" ? "Ollama 已完成分析。以下為 AI 生成說明，請與原始建議及注意事項一起閱讀。" : result.localAI.message}</p>
            {result.localAI.explanation ? <div className="mt-4 space-y-3 leading-7">{result.localAI.explanation.split(/\n\s*\n/).map((paragraph, index) => <p className="whitespace-pre-wrap" key={index}>{paragraph.replace(/^#{1,6}\s+/gm, "").replace(/\*\*([^*]+)\*\*/g, "$1")}</p>)}</div> : null}
          </section>
        ) : null}
        {error ? <div className="rounded-md border border-red-200 bg-red-50 p-4 text-red-700">{error}</div> : null}

        {screen === "questionnaire" ? (
          <QuestionnaireManual
            chronicConditions={chronicConditions}
            healthGoals={healthGoals}
            isLoading={isLoading}
            onAnalyze={handleAnalyze}
            profile={profile}
            setChronicConditions={setChronicConditions}
            setHealthGoals={setHealthGoals}
            setProfile={setProfile}
            setSpecialGroups={setSpecialGroups}
            setStep={setStep}
            setSymptomTags={setSymptomTags}
            specialGroups={specialGroups}
            step={step}
            symptomTags={symptomTags}
            toggleArrayValue={toggleArrayValue}
            toggleDietHabit={toggleDietHabit}
          />
        ) : null}

        {screen === "results" ? (
          result ? (
            <ResultsManual result={result} setScreen={setScreen} />
          ) : (
            <EmptyResult goQuestionnaire={() => setScreen("questionnaire")} />
          )
        ) : null}

        {screen === "supplements" ? (
          <SupplementManual
            filteredProducts={filteredProducts}
            productSearch={productSearch}
            setProductSearch={setProductSearch}
            supplements={supplements}
            toggleSupplement={toggleSupplement}
          />
        ) : null}

        <FooterNotes />
      </div>
    </main>
  );
}

function Hero({ result }: { result: AnalyzeResponse | null }) {
  const score = result ? calculateScore(result) : 82;
  return (
    <section className="grid gap-6 overflow-hidden rounded-md border border-slate-200 bg-white p-6 shadow-sm lg:grid-cols-[1.05fr_0.95fr]">
      <div className="flex flex-col justify-center">
        <div className="inline-flex w-fit items-center gap-3 rounded-full bg-slate-50 px-4 py-2 text-sm font-semibold text-slate-700">
          <span className="grid h-8 w-8 place-items-center rounded-full border border-leaf text-leaf">AI</span>
          Food data science and consumer analysis
        </div>
        <h1 className="mt-5 text-5xl font-bold leading-tight tracking-normal md:text-6xl">
          Nutri<span className="text-leaf">Match</span>
        </h1>
        <p className="mt-3 text-3xl font-bold">Personalized nutrition advice system</p>
        <p className="mt-4 max-w-2xl leading-7 text-slate-600">
          透過四步問卷，整理營養優先建議、食物來源與補充品注意事項。可選擇本地 Ollama，進一步取得中文解讀。
        </p>
        <div className="mt-6 grid gap-3 sm:grid-cols-4">
          <FeatureIcon label="AI analysis" icon="AI" />
          <FeatureIcon label="Food sources" icon="F" />
          <FeatureIcon label="Supplement stack" icon="S" />
          <FeatureIcon label="Local Ollama" icon="L" />
        </div>
      </div>
      <div className="relative min-h-[340px]">
        <div className="absolute left-3 top-10 h-64 w-[78%] rounded-md border border-slate-200 bg-slate-900 p-3 shadow-2xl">
          <div className="grid h-full grid-cols-[80px_1fr] gap-3 rounded bg-white p-3">
            <div className="rounded bg-[#0c3328] p-3 text-xs font-semibold text-white">
              <p>NutriMatch</p>
              <div className="mt-8 grid gap-3 text-emerald-100">
                <span>Survey</span>
                <span>Results</span>
                <span>Stack · 示意</span>
              </div>
            </div>
            <div className="grid gap-3">
              <div className="grid grid-cols-[130px_1fr] gap-3">
                <ScoreRing score={score} size="large" />
                <MiniTrend />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <MiniBars />
                <MiniList />
              </div>
            </div>
          </div>
        </div>
        <div className="absolute bottom-2 right-5 h-72 w-36 rounded-[28px] border-8 border-slate-900 bg-white p-3 shadow-2xl">
          <div className="mx-auto mb-3 h-1 w-12 rounded bg-slate-300" />
          <p className="text-sm font-bold">NutriMatch</p>
          <div className="mt-4 grid gap-2">
            {["B Complex", "Magnesium", "Omega-3", "Vitamin D", "Lutein"].map((item) => (
              <div className="flex items-center gap-2 rounded border border-slate-100 p-2 text-xs" key={item}>
                <span className="h-2 w-2 rounded-full bg-leaf" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function ProcessStrip() {
  return (
    <section className="rounded-md border border-slate-200 bg-white p-4 shadow-sm">
      <div className="grid gap-3 md:grid-cols-5">
        <ProcessItem index="1" title="Profile" body="Enter basic data and habits" />
        <ProcessItem index="2" title="Groups" body="Select identity-based groups" />
        <ProcessItem index="3" title="Symptoms" body="Describe current lifestyle states" />
        <ProcessItem index="4" title="Results" body="View visual nutrition advice" />
        <ProcessItem index="5" title="Stack" body="Manage DHC products separately" />
      </div>
    </section>
  );
}

function QuestionnaireManual(props: {
  chronicConditions: ChronicCondition[];
  healthGoals: HealthGoal[];
  isLoading: boolean;
  onAnalyze: () => void;
  profile: BasicProfile;
  setChronicConditions: (next: ChronicCondition[]) => void;
  setHealthGoals: (next: HealthGoal[]) => void;
  setProfile: (next: BasicProfile) => void;
  setSpecialGroups: (next: SpecialGroup[]) => void;
  setStep: (next: number) => void;
  setSymptomTags: (next: SymptomTag[]) => void;
  specialGroups: SpecialGroup[];
  step: number;
  symptomTags: SymptomTag[];
  toggleArrayValue: <T extends string>(value: T, values: T[], setter: (next: T[]) => void) => void;
  toggleDietHabit: (value: DietHabit) => void;
}) {
  const isLastStep = props.step === steps.length - 1;
  return (
    <section className="grid gap-6 lg:grid-cols-[240px_1fr]">
      <aside className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
        <SectionLabel text="Workflow" />
        <div className="mt-5 grid gap-4">
          {steps.map((label, index) => (
            <button
              className={`flex items-center gap-3 rounded-md border p-3 text-left ${props.step === index ? "border-leaf bg-emerald-50" : "border-slate-200 bg-white"}`}
              key={label}
              onClick={() => props.setStep(index)}
              type="button"
            >
              <span className="grid h-8 w-8 place-items-center rounded-full bg-leaf text-sm font-bold text-white">{index + 1}</span>
              <span className="font-semibold">{label}</span>
            </button>
          ))}
        </div>
      </aside>

      <div className="rounded-md border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-medium text-leaf">Questionnaire {props.step + 1}/4</p>
        <h2 className="mt-1 text-2xl font-semibold">{steps[props.step]}</h2>
        <div className="mt-6">
          {props.step === 0 ? <BasicProfileStep {...props} /> : null}
          {props.step === 1 ? <SpecialGroupsStep {...props} /> : null}
          {props.step === 2 ? (
            <CheckboxGroup
              items={SYMPTOM_TAGS}
              selected={props.symptomTags}
              title="Symptoms and lifestyle states"
              toggle={(value) => props.toggleArrayValue(value, props.symptomTags, props.setSymptomTags)}
            />
          ) : null}
          {props.step === 3 ? (
            <CheckboxGroup
              items={HEALTH_GOALS}
              selected={props.healthGoals}
              title="Health goals"
              toggle={(value) => props.toggleArrayValue(value, props.healthGoals, props.setHealthGoals)}
            />
          ) : null}
        </div>
        <div className="mt-8 flex items-center justify-between">
          <button className="h-10 rounded-md border border-slate-300 px-4 font-semibold text-slate-700 disabled:opacity-40" disabled={props.step === 0} onClick={() => props.setStep(props.step - 1)} type="button">
            Back
          </button>
          {isLastStep ? (
            <button className="h-10 rounded-md bg-leaf px-5 font-semibold text-white disabled:bg-slate-400" disabled={props.isLoading} onClick={props.onAnalyze} type="button">
              {props.isLoading ? "Analyzing" : "View results"}
            </button>
          ) : (
            <button className="h-10 rounded-md bg-leaf px-5 font-semibold text-white" onClick={() => props.setStep(props.step + 1)} type="button">
              Next
            </button>
          )}
        </div>
      </div>
    </section>
  );
}

function BasicProfileStep({
  profile,
  setProfile,
  toggleDietHabit
}: {
  profile: BasicProfile;
  setProfile: (next: BasicProfile) => void;
  toggleDietHabit: (value: DietHabit) => void;
}) {
  return (
    <div className="grid gap-6">
      <div className="grid gap-3 sm:grid-cols-2">
        <NumberField label="Age" value={profile.age} min={1} max={120} onChange={(age) => setProfile({ ...profile, age })} />
        <label className="grid gap-1 text-sm font-semibold text-slate-700">
          Biological sex
          <select className="h-10 rounded-md border border-slate-300 px-3 font-normal" onChange={(event) => setProfile({ ...profile, sex: event.target.value as BasicProfile["sex"] })} value={profile.sex}>
            <option value="female">Female</option>
            <option value="male">Male</option>
            <option value="other">Other</option>
          </select>
        </label>
        <NumberField label="Height cm" value={profile.height_cm} min={80} max={230} onChange={(height_cm) => setProfile({ ...profile, height_cm })} />
        <NumberField label="Weight kg" value={profile.weight_kg} min={20} max={300} onChange={(weight_kg) => setProfile({ ...profile, weight_kg })} />
        <NumberField label="Exercise per week" value={profile.exercise_frequency_per_week} min={0} max={14} onChange={(exercise_frequency_per_week) => setProfile({ ...profile, exercise_frequency_per_week })} />
        <NumberField label="Water L/day" value={profile.water_liters_per_day} min={0} max={8} step={0.1} onChange={(water_liters_per_day) => setProfile({ ...profile, water_liters_per_day })} />
      </div>
      <CheckboxGroup items={ROUTINES} radioValue={profile.routine} title="Routine" toggle={(value) => setProfile({ ...profile, routine: value as Routine })} />
      <CheckboxGroup items={DIET_HABITS} selected={profile.diet_habits} title="Diet habits" toggle={toggleDietHabit} />
    </div>
  );
}

function SpecialGroupsStep({
  chronicConditions,
  setChronicConditions,
  setSpecialGroups,
  specialGroups,
  toggleArrayValue
}: {
  chronicConditions: ChronicCondition[];
  setChronicConditions: (next: ChronicCondition[]) => void;
  setSpecialGroups: (next: SpecialGroup[]) => void;
  specialGroups: SpecialGroup[];
  toggleArrayValue: <T extends string>(value: T, values: T[], setter: (next: T[]) => void) => void;
}) {
  return (
    <div className="grid gap-6">
      <CheckboxGroup items={SPECIAL_GROUPS} selected={specialGroups} title="Special groups" toggle={(value) => toggleArrayValue(value, specialGroups, setSpecialGroups)} />
      {specialGroups.includes("chronic_patient") ? (
        <CheckboxGroup items={CHRONIC_CONDITIONS} selected={chronicConditions} title="Chronic conditions" toggle={(value) => toggleArrayValue(value, chronicConditions, setChronicConditions)} />
      ) : null}
    </div>
  );
}

function ResultsManual({ result, setScreen }: { result: AnalyzeResponse; setScreen: (screen: Screen) => void }) {
  const score = calculateScore(result);
  const topThree = result.nutrientRecommendations.slice(0, 3);
  const selectedProducts = result.currentSupplementReview.map((review) => DHC_PRODUCTS.find((product) => product.id === review.productId)).filter(Boolean) as typeof DHC_PRODUCTS;

  return (
    <section className="grid gap-6 lg:grid-cols-[1fr_1fr]">
      <div className="grid content-start gap-5">
        <SectionLabel text="Core analysis" />
        <div className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
          <div className="grid gap-4 md:grid-cols-[160px_1fr]">
            <ScoreRing score={score} size="large" />
            <div>
              <h2 className="text-xl font-semibold">推薦摘要 · 示意指標</h2>
              <p className="mt-1 text-sm text-slate-500">以下為上次送出資料的報告。此指標不是健康分數或疾病機率。</p>
              <p className="mt-2 leading-7 text-slate-700">{result.profileDescription}</p>
              <div className="mt-4 h-3 overflow-hidden rounded-full bg-slate-100">
                <div className="h-full rounded-full bg-gradient-to-r from-leaf via-amberline to-coral" style={{ width: `${score}%` }} />
              </div>
            </div>
          </div>
        </div>
        <RankingCard title="Top 3 focus nutrients" items={topThree} />
        <FoodCard items={topThree} />
        <div className="rounded-md border border-amber-200 bg-amber-50 p-5">
          <h2 className="text-lg font-semibold">安全提醒</h2>
          <p className="mt-2 text-sm">營養教育原型，不能診斷疾病；慢性病、孕期或用藥者請諮詢醫師或營養師。</p>
          {result.safetyNotes.map((note, index) => <p className="mt-2 text-sm" key={index}>{note}</p>)}
          {result.currentSupplementReview.map((review) => <div className="mt-3 text-sm" key={review.productId}><strong>{review.productName}</strong><p>{review.comment}</p>{review.caution ? <p>{review.caution}</p> : null}</div>)}
        </div>
        <div className="rounded-md border border-slate-200 bg-white p-5">
          <h2 className="text-lg font-semibold">推薦原因與注意事項</h2>
          {result.nutrientRecommendations.map((advice) => <details className="mt-3 border-t border-slate-100 pt-3" key={advice.nutrient}><summary className="cursor-pointer font-semibold">{advice.nutrient} · 優先度 {Math.round(advice.score * 100)}</summary><p className="mt-2 leading-7">{advice.whyNeeded}</p><p className="mt-2 text-sm">食物來源：{advice.foodSources.join("、")}</p><p className="mt-2 text-sm">補充時間：{advice.intakeTiming}</p>{advice.caution ? <p className="mt-2 text-sm text-amber-800">注意：{advice.caution}</p> : null}</details>)}
        </div>
      </div>
      <div className="grid content-start gap-5">
        <SectionLabel text="Visual results" />
        <RankingCard title="Top 8 nutrient priorities" items={result.nutrientRecommendations} bars />
        <div className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold">Radar summary</h2>
          <RadarGraphic items={result.nutrientRecommendations.slice(0, 6)} />
        </div>
        <div className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-lg font-semibold">Supplement manager included</h2>
            <button className="rounded-md border border-slate-300 px-3 py-2 text-sm font-semibold" onClick={() => setScreen("supplements")} type="button">Manage</button>
          </div>
          {selectedProducts.length ? (
            <>
              {result.coveredNutrients.length ? (
                <div className="mt-4 rounded-md bg-emerald-50 p-3 text-sm text-emerald-800">
                  Covered by your supplement stack: {result.coveredNutrients.join(" / ")}
                </div>
              ) : null}
              <div className="mt-4 grid gap-3 sm:grid-cols-2">{selectedProducts.map((product) => <ProductMiniCard key={product.id} product={product} selected />)}</div>
            </>
          ) : (
            <p className="mt-3 text-sm text-slate-500">No daily supplements selected.</p>
          )}
        </div>
      </div>
    </section>
  );
}

function RankingCard({ bars, items, title }: { bars?: boolean; items: AnalyzeResponse["nutrientRecommendations"]; title: string }) {
  return (
    <div className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold">{title}</h2>
      <div className="mt-4 grid gap-3">
        {items.map((item, index) => (
          <div className="grid grid-cols-[28px_1fr_70px] items-center gap-3" key={item.nutrient}>
            <span className="grid h-7 w-7 place-items-center rounded-full bg-leaf text-sm font-bold text-white">{index + 1}</span>
            <div>
              <p className="font-semibold">{item.nutrient}</p>
              {bars ? <div className="mt-1 h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-leaf" style={{ width: `${Math.round(item.score * 100)}%` }} /></div> : null}
            </div>
            <span className="text-right text-sm text-slate-500">{Math.round(item.score * 100)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function FoodCard({ items }: { items: AnalyzeResponse["nutrientRecommendations"] }) {
  return (
    <div className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold">Food source suggestions</h2>
      <div className="mt-4 grid gap-3">
        {items.map((item) => <div className="rounded-md bg-slate-50 p-3" key={item.nutrient}><p className="font-semibold">{item.nutrient}</p><p className="mt-1 text-sm text-slate-600">{item.foodSources.join(" / ")}</p></div>)}
      </div>
    </div>
  );
}

function SupplementManual({ filteredProducts, productSearch, setProductSearch, supplements, toggleSupplement }: { filteredProducts: typeof DHC_PRODUCTS; productSearch: string; setProductSearch: (next: string) => void; supplements: SupplementUse[]; toggleSupplement: (productId: string) => void }) {
  return (
    <section className="grid gap-6 lg:grid-cols-[300px_1fr]">
      <aside className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
        <SectionLabel text="Supplement manager" />
        <p className="mt-4 leading-7 text-slate-600">Optional feature. Select daily DHC products; they are included in duplicate nutrient and caution checks.</p>
        <input className="mt-5 h-11 w-full rounded-md border border-slate-300 px-3" onChange={(event) => setProductSearch(event.target.value)} placeholder="Search products" value={productSearch} />
        <p className="mt-4 text-sm text-slate-500">Selected {supplements.length}</p>
      </aside>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{filteredProducts.map((product) => {
        const selected = supplements.some((item) => item.product_id === product.id);
        return <button className="text-left" key={product.id} onClick={() => toggleSupplement(product.id)} type="button"><ProductMiniCard product={product} selected={selected} /></button>;
      })}</div>
    </section>
  );
}

function ProductMiniCard({ product, selected }: { product: (typeof DHC_PRODUCTS)[number]; selected: boolean }) {
  return (
    <article className={`overflow-hidden rounded-md border bg-white shadow-sm transition ${selected ? "border-leaf ring-2 ring-emerald-100" : "border-slate-200"}`}>
      <div className="flex h-40 items-center justify-center bg-slate-50"><div className="grid h-28 w-20 place-items-center rounded-sm border border-slate-200 bg-white text-center shadow-sm"><span className="font-bold text-leaf">DHC</span><span className="text-xs text-slate-500">示例品項</span></div></div>
      <div className="p-4"><div className="flex items-start justify-between gap-3"><h3 className="font-semibold">{product.name}</h3><span className={`rounded-full px-2 py-1 text-xs font-semibold ${selected ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>{selected ? "Added" : "Add"}</span></div><p className="mt-2 text-sm text-slate-500">{product.dosage}</p><p className="mt-1 text-xs text-slate-400">{product.nutrients.slice(0, 3).join(" / ")}</p></div>
    </article>
  );
}

function RadarGraphic({ items }: { items: AnalyzeResponse["nutrientRecommendations"] }) {
  const point = (index: number, scale: number) => {
    const angle = index * 2 * Math.PI / Math.max(items.length, 1) - Math.PI / 2;
    return `${110 + 85 * scale * Math.cos(angle)},${110 + 85 * scale * Math.sin(angle)}`;
  };
  return (
    <div className="grid gap-3 md:grid-cols-[220px_1fr]">
      <svg viewBox="0 0 220 220" role="img" aria-label="營養建議優先度雷達圖，依右側順序順時針排列" className="mx-auto h-52 w-52">{[0.25, 0.5, 0.75, 1].map((level) => <polygon key={level} points={items.map((_, index) => point(index, level)).join(" ")} fill="none" stroke="#cbd5e1" />)}{items.map((item, index) => <line key={item.nutrient} x1="110" y1="110" x2={point(index, 1).split(",")[0]} y2={point(index, 1).split(",")[1]} stroke="#e2e8f0" />)}<polygon points={items.map((item, index) => point(index, item.score)).join(" ")} fill="#4f9b5e" fillOpacity="0.25" stroke="#4f9b5e" strokeWidth="2" /></svg>
      <div className="grid gap-2">{items.map((item) => <div className="grid grid-cols-[90px_1fr_42px] items-center gap-3" key={item.nutrient}><span className="text-sm font-semibold">{item.nutrient}</span><div className="h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-leaf" style={{ width: `${Math.round(item.score * 100)}%` }} /></div><span className="text-right text-xs text-slate-500">{Math.round(item.score * 100)}</span></div>)}</div>
    </div>
  );
}

function EmptyResult({ goQuestionnaire }: { goQuestionnaire: () => void }) {
  return <section className="flex min-h-96 flex-col items-center justify-center rounded-md border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600"><p>No result yet. Please complete the staged questionnaire first.</p><button className="mt-4 h-10 rounded-md bg-leaf px-4 font-semibold text-white" onClick={goQuestionnaire} type="button">Start questionnaire</button></section>;
}

function ProcessItem({ body, index, title }: { body: string; index: string; title: string }) {
  return <div className="relative rounded-md border border-slate-100 p-4"><span className="grid h-8 w-8 place-items-center rounded-full bg-leaf text-sm font-bold text-white">{index}</span><h3 className="mt-3 font-semibold">{title}</h3><p className="mt-2 text-sm leading-6 text-slate-500">{body}</p></div>;
}

function SectionLabel({ text }: { text: string }) {
  return <h2 className="inline-flex bg-[#0b5a3d] px-4 py-2 text-lg font-bold text-white">{text}</h2>;
}

function FeatureIcon({ icon, label }: { icon: string; label: string }) {
  return <div className="text-center"><div className="mx-auto grid h-14 w-14 place-items-center rounded-full border border-leaf bg-emerald-50 text-lg font-bold text-leaf">{icon}</div><p className="mt-2 text-sm font-semibold">{label}</p></div>;
}

function ScoreRing({ score, size = "small" }: { score: number; size?: "small" | "large" }) {
  const dimension = size === "large" ? "h-32 w-32" : "h-24 w-24";
  return <div className={`${dimension} grid place-items-center rounded-full`} style={{ background: `conic-gradient(#4f9b5e ${score * 3.6}deg, #e7eee8 0deg)` }}><div className="grid h-[76%] w-[76%] place-items-center rounded-full bg-white text-center"><div><p className="text-3xl font-bold text-leaf">{score}</p><p className="text-xs text-slate-500">/100</p></div></div></div>;
}

function MiniTrend() {
  return <div className="rounded-md border border-slate-100 p-3"><p className="text-xs font-semibold text-slate-500">Demo trend</p><div className="mt-6 flex h-16 items-end gap-2">{[35, 52, 45, 72, 58, 80, 66].map((height) => <span className="w-full rounded bg-leaf/70" key={height} style={{ height: `${height}%` }} />)}</div></div>;
}

function MiniBars() {
  return <div className="rounded-md border border-slate-100 p-3"><p className="text-xs font-semibold text-slate-500">Demo distribution</p><div className="mt-4 grid gap-2">{[82, 68, 54, 72].map((width) => <div className="h-2 rounded bg-slate-100" key={width}><div className="h-full rounded bg-leaf" style={{ width: `${width}%` }} /></div>)}</div></div>;
}

function MiniList() {
  return <div className="rounded-md border border-slate-100 p-3 text-xs"><p className="font-semibold text-slate-500">Top advice</p><div className="mt-3 grid gap-2">{["B Complex", "Magnesium", "Omega-3"].map((item) => <div className="flex items-center gap-2" key={item}><span className="h-2 w-2 rounded-full bg-leaf" /><span>{item}</span></div>)}</div></div>;
}

function TopButton({ active, children, disabled, onClick }: { active: boolean; children: ReactNode; disabled?: boolean; onClick: () => void }) {
  return <button className={`h-10 rounded-md px-4 font-semibold disabled:cursor-not-allowed disabled:opacity-40 ${active ? "bg-leaf text-white" : "border border-slate-300 bg-white text-slate-700"}`} disabled={disabled} onClick={onClick} type="button">{children}</button>;
}

function NumberField({ label, max, min, onChange, step = 1, value }: { label: string; max: number; min: number; onChange: (value: number) => void; step?: number; value: number }) {
  return <label className="grid gap-1 text-sm font-semibold text-slate-700">{label}<input className="h-10 rounded-md border border-slate-300 px-3 font-normal" max={max} min={min} onChange={(event) => onChange(Number(event.target.value))} step={step} type="number" value={value} /></label>;
}

function CheckboxGroup<T extends string>({ items, radioValue, selected, title, toggle }: { items: Array<{ key: T; label: string }>; radioValue?: T; selected?: T[]; title: string; toggle: (value: T) => void }) {
  return <div><h3 className="text-sm font-semibold text-slate-700">{title}</h3><div className="mt-3 grid gap-2 sm:grid-cols-2">{items.map((item) => {
    const checked = radioValue ? radioValue === item.key : Boolean(selected?.includes(item.key));
    return <label className="flex min-h-10 items-center gap-3 rounded-md border border-slate-200 px-3 text-sm" key={item.key}><input checked={checked} className="h-4 w-4 accent-leaf" onChange={() => toggle(item.key)} type={radioValue ? "radio" : "checkbox"} /><span>{item.label}</span></label>;
  })}</div></div>;
}

function FooterNotes() {
  return <footer className="grid gap-4 border-t border-slate-200 py-6 text-sm text-slate-600 md:grid-cols-2"><div><h2 className="font-semibold text-ink">Notes</h2><ul className="mt-2 list-disc space-y-1 pl-5"><li>This system provides nutrition suggestions, not medical diagnosis.</li><li>Special groups and symptoms are intentionally separated in the questionnaire.</li><li>Supplement manager data is included in analysis but remains optional.</li></ul></div><div><h2 className="font-semibold text-ink">Data sources</h2><ul className="mt-2 list-disc space-y-1 pl-5"><li>DHC product catalog and dosage references</li><li>Personalized questionnaire rules</li><li>Food source and nutrient advice database</li></ul></div></footer>;
}

function calculateScore(result: AnalyzeResponse) {
  const average = result.nutrientRecommendations.reduce((sum, item) => sum + item.score, 0) / Math.max(result.nutrientRecommendations.length, 1);
  return Math.max(1, Math.min(99, Math.round(100 - average * 25)));
}
