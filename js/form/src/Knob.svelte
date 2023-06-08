<script context="module">
	let _id = 0;
</script>

<script lang="ts">
	import { createEventDispatcher, afterUpdate } from "svelte";
	import { BlockTitle } from "@gradio/atoms";

	export let value: number = 0;
	export let value_is_output: boolean = false;
	export let minimum: number = 0;
	export let maximum: number = 100;
	export let step: number = 1;
	export let disabled: boolean = false;
	export let label: string;
	export let info: string | undefined = undefined;
	export let show_label: boolean;

	const id = `range_id_${_id++}`;
	const dispatch = createEventDispatcher<{
		change: number;
		input: undefined;
		release: number;
	}>();

	function handle_change() {
		dispatch("change", value);
		if (!value_is_output) {
			dispatch("input");
		}
	}
	afterUpdate(() => {
		value_is_output = false;
	});
	$: value, handle_change();

	function handle_release(e: MouseEvent) {
		dispatch("release", value);
	}
	const clamp = () => {
		dispatch("release", value);
		value = Math.min(Math.max(value, minimum), maximum);
	};

	// --------------------------------------------------------------------------

	const SCALE = 100;

	const MID_X = SCALE / 2;
	const MID_Y = SCALE / 2;

	const GAP_ANGLE = 75;
	const MIN_ANGLE = GAP_ANGLE / 2;
	const MAX_ANGLE = 360 - GAP_ANGLE / 2;

	export let responsive = false;

	export let size = 50;

	export let textColor = "#000000";
	export let lineColor = "#409eff";
	export let lineBackgroundColor = "#dcdfe6";
	export let lineWidth = 8;

	export let sensitivity = 200;

	let capturedValue = 0;
	let capturedMovement = 0;

	$: svgSize = responsive ? size + "%" : size;

	$: arcFullPath = ccwArcPath(radius, MIN_ANGLE, MAX_ANGLE);
	$: arcValuePath = ccwArcPath(radius, originAngle, valueAngle);

	$: valueAngle = valueToAngle(value);
	$: originAngle = minimum <= 0 && maximum >= 0 ? valueToAngle(0) : MIN_ANGLE;

	// radius goes to the middle of the stroke path, so subtract
	// half of the stroke width to make it touch the view box
	$: radius = Math.floor(SCALE / 2 - lineWidth / 2);

	function valueToAngle(value: number): number {
		const valueNorm = (value - minimum) / (maximum - minimum);
		const angleRange = 360 - GAP_ANGLE;
		const angleDelta = valueNorm * angleRange;
		const angle = MIN_ANGLE + angleDelta;
		return angle;
	}

	function angleToPoint(radius: number, angleDeg: number) {
		// consider point at 270 deg to be origin to avoid wrap around angles
		const angleRad = ((angleDeg - 270) * Math.PI) / 180;

		return {
			x: MID_X + radius * Math.cos(angleRad),
			y: MID_Y + radius * Math.sin(angleRad)
		};
	}

	function ccwArcPath(
		radius: number,
		startAngle: number,
		endAngle: number
	): string {
		if (endAngle < startAngle) {
			const temp = startAngle;
			startAngle = endAngle;
			endAngle = temp;
		}

		const startPt = angleToPoint(radius, startAngle);
		const endPt = angleToPoint(radius, endAngle);

		const largeArcFlag = endAngle - startAngle > 180 ? 1 : 0;
		const sweepFlag = 1;

		const arcPath =
			`M ${startPt.x} ${startPt.y} ` +
			`A ${radius} ${radius} ` +
			`0 ${largeArcFlag} ${sweepFlag} ` +
			`${endPt.x} ${endPt.y}`;
		return arcPath;
	}

	function onPointerDown(e: PointerEvent): void {
		if (!disabled) {
			e.preventDefault();

			capturedValue = value;
			capturedMovement = 0;

			window.addEventListener("pointermove", onPointerMove);
			window.addEventListener("pointerup", onPointerUp);
		}
	}

	function onPointerUp(e: PointerEvent): void {
		if (!disabled) {
			e.preventDefault();

			window.removeEventListener("pointermove", onPointerMove);
			window.removeEventListener("pointerup", onPointerUp);

			dispatch("release", value);
		}
	}

	function onPointerMove(e: PointerEvent): void {
		if (!disabled) {
			e.preventDefault();

			capturedMovement -= e.movementY;

			const movementStep = (maximum - minimum) / sensitivity;

			let newValue = capturedValue + capturedMovement * movementStep;
			if (newValue < minimum) {
				newValue = minimum;
			} else if (newValue > maximum) {
				newValue = maximum;
			}
			// value = Math.min(Math.max(value, minimum), maximum);

			// round to step
			value = Math.round((newValue - minimum) / step) * step + minimum;

			dispatch("change", value);
			if (!value_is_output) {
				dispatch("input");
			}
		}
	}
</script>

<div class="wrap">
	<label for={id}>
		<BlockTitle {show_label} {info}>{label}</BlockTitle>
	</label>
</div>

<svg
	width={svgSize}
	height={svgSize}
	viewBox="0 0 {SCALE} {SCALE}"
	class="knob"
	on:pointerdown={onPointerDown}
>
	<path
		d={arcFullPath}
		stroke={lineBackgroundColor}
		stroke-width={lineWidth}
		fill="none"
	/>
	<path
		d={arcValuePath}
		stroke={lineColor}
		stroke-width={lineWidth}
		fill="none"
	/>
	<text x="50%" y="56%" text-anchor="middle" fill={textColor} class="knob-text"
		>{value}</text
	>
</svg>

<input
	{id}
	data-testid="number-input"
	type="number"
	bind:value
	min={minimum}
	max={maximum}
	on:blur={clamp}
	{step}
	{disabled}
	on:pointerup={handle_release}
/>

<style>
	.wrap {
		display: flex;
		flex-direction: column;
		width: 100%;
	}

	.knob {
		cursor: pointer;
	}

	.knob-text {
		font-size: 1.5rem;
		user-select: none;
	}

	input[type="number"] {
		display: block;
		position: relative;
		outline: none !important;
		box-shadow: var(--input-shadow);
		border: var(--input-border-width) solid var(--input-border-color);
		border-radius: var(--input-radius);
		background: var(--input-background-fill);
		padding: var(--size-2) var(--size-2);
		height: var(--size-6);
		color: var(--body-text-color);
		font-size: var(--input-text-size);
		line-height: var(--line-sm);
		text-align: center;
	}
	input:disabled {
		-webkit-text-fill-color: var(--body-text-color);
		-webkit-opacity: 1;
		opacity: 1;
	}

	input[type="number"]:focus {
		box-shadow: var(--input-shadow-focus);
		border-color: var(--input-border-color-focus);
	}

	input::placeholder {
		color: var(--input-placeholder-color);
	}

	input[disabled] {
		cursor: not-allowed;
	}
</style>
