#!/usr/bin/env ruby
# frozen_string_literal: true

# Checks the structured diagnostic YAML files against the screenshot-derived
# Game Settings catalog. The catalog remains authoritative for visible rows,
# order and native defaults; YAML remains authoritative for offsets, encodings
# and integrity details that are not visible in screenshots.

require "pathname"
require "set"
require "yaml"
require "json"
require "digest"

ROOT = Pathname.new(__dir__).parent.realpath
CATALOG_PATH = ROOT / "GAME_SETTINGS_CATALOG.md"
YAML_ROOT = ROOT / "data/diagnostic-menus"
EXPECTED_YAML_COUNT = 56

def catalog_rows
  catalog = {}
  current = nil
  CATALOG_PATH.each_line do |line|
    if (match = line.match(/^### .* \(`([^`]+)`\)$/))
      current = match[1]
      catalog[current] = []
    elsif current && line.match?(/^\| \d+ \|/)
      cells = line.strip.delete_prefix("|").delete_suffix("|").split("|").map(&:strip)
      catalog[current] << {label: cells[1], default: cells[2], values: cells[3]}
    end
  end
  catalog
end

def labelled_rows(value)
  case value
  when Hash
    rows = value["label"] && value["key"] && !value["options"].is_a?(Array) ? [value] : []
    rows + value.values.flat_map { |child| labelled_rows(child) }
  when Array
    value.flat_map { |child| labelled_rows(child) }
  else
    []
  end
end

def visible_rows(data, catalog)
  game = data.dig("game", "set")
  menu = data["menus"] || {}
  inherited = labelled_rows(menu).select { |row| row["label"] }

  reference = menu.values.map do |entry|
    entry["inherited_editable_options_from"] if entry.is_a?(Hash)
  end.compact.first
  if reference
    extra = inherited.reject { |row| row["coding_reference"] }
    return catalog.fetch(reference).map { |row| {"label" => row[:label]} } + extra
  end

  if inherited.empty? && data.dig("verification", "menu_parameters") == "identical_to_parent"
    return catalog.fetch(data.dig("game", "parent")).map { |row| {"label" => row[:label]} }
  end

  positioned, ordinary = inherited.partition { |row| row["visible_position"] }
  positioned.sort_by { |row| row["visible_position"] }.each do |row|
    ordinary.insert(row["visible_position"].to_i - 1, row)
  end
  if (extension = data["ride_color_extension"])
    # Preserve the pinned historical menu inventory while comparing the current
    # independently documented four-color selector against the live catalogue.
    ordinary = ordinary.map do |row|
      row["key"] == "ride_id" ? row.merge("values" => extension.fetch("values")) : row
    end
  end
  ordinary
end

def rendered(value)
  case value
  when true then "ON"
  when false then "OFF"
  when Hash
    value.key?("setting") ? "##{value['setting']}" : value.values.join(" / ")
  else
    value.to_s
  end
end

def normalized(value)
  value.to_s.upcase
       .gsub(/U\.?S\.?A?\.?\b/, "USA")
       .gsub(/\bJPN\b/, "JAPAN")
       .gsub(/\bEXP\b/, "EXPORT")
       .gsub(/C\.?R\.?T\.?/, "CRT")
       .gsub(/\bINITIAL\b|\bMAX(?: LIFE)?\b/, "")
       .gsub(/[^A-Z0-9#+-]+/, " ").strip
end

def documented_values(cell)
  return [] if ["—", "nessun ciclo dedicato", "non acquisiti"].include?(cell)
  cell.split(",").map(&:strip)
end

catalog = catalog_rows
errors = []
checked = 0
paths = Dir[YAML_ROOT.join("*.yaml")].sort
errors << "expected #{EXPECTED_YAML_COUNT} diagnostic YAML files, found #{paths.length}" unless paths.length == EXPECTED_YAML_COUNT
seen_games = Set.new

paths.each do |path|
  data = YAML.safe_load(File.read(path), permitted_classes: [], aliases: true)
  game = data.dig("game", "set")
  errors << "#{File.basename(path)}: duplicate game #{game.inspect}" unless seen_games.add?(game)
  errors << "#{File.basename(path)}: filename does not match game #{game.inspect}" unless File.basename(path, ".yaml") == game
  expected = catalog[game]
  unless expected
    errors << "#{File.basename(path)}: no catalog section for #{game.inspect}"
    next
  end

  if data.dig("verification", "status") == "acquisition_pending"
    errors << "#{game}: pending acquisition cannot declare setting rows" unless (data["menus"] || {}).empty?
    %w[storage_offsets encodings game_checksum initial_template automatic_overrides].each do |gate|
      errors << "#{game}: missing pending gate #{gate}" unless data.dig("verification", "pending").include?(gate)
    end
    recipe = ROOT / data.dig("verification", "persistent_script")
    errors << "#{game}: missing acquisition recipe" unless recipe.file?
  end

  if (ride = data["ride_id_campaign"] || data["historical_ride_id_campaign"])
    errors << "#{game}: Ride ID must retain unverified defaults/mapping" unless ride["native_default"] == "unverified" && ride["storage_mapping"] == "unverified"
    observation_path = ROOT / ride["evidence"]
    if observation_path.file?
      observations = JSON.parse(observation_path.read)
      record = observations.fetch("sets").fetch(game)
      errors << "#{game}: Ride ID observed cycle differs from evidence" unless ride["observed_values"] == record["observed_values"] && ride["cycle_closed"] == record["cycle_closed"]
      errors << "#{game}: Ride ID fresh reload differs from evidence" unless ride["fresh_reload"] == record.dig("commit", "fresh_reload_value") && record.dig("commit", "verified")
      record["screenshots"].each do |relative, hash|
        image = observation_path.dirname / relative
        errors << "#{game}: missing/changed Ride ID screenshot #{relative}" unless image.file? && Digest::SHA256.file(image).hexdigest == hash
      end
    end
  end

  errors << "powsledm: missing Main operator inventory" if game == "powsledm" && !data.key?("main_operator_inventory")
  if (inventory = data["main_operator_inventory"])
    errors << "#{game}: Main inventory must remain unverified for defaults/ranges" unless game == "powsledm" && inventory["native_defaults"] == "unverified" && inventory["complete_ranges_and_cycles"] == "unverified" && inventory["committed_presets"] == "none"
    errors << "#{game}: Main inventory must contain 15 separately observed fields" unless inventory.fetch("fields").length == 15
    observation_path = ROOT / inventory.fetch("evidence")
    if observation_path.file?
      observations = JSON.parse(observation_path.read)
      errors << "#{game}: Main inventory differs from screenshot record" unless inventory["fields"] == observations["fields"]
      inventory["fields"].each do |field|
        errors << "#{game}: missing Main inventory screenshot #{field['evidence']}" unless (observation_path.dirname / field.fetch("evidence")).file?
      end
    end
  end

  if (campaign = data["operator_settings_campaign"])
    errors << "#{game}: calibration must be listed only" unless campaign.dig("calibration", "policy") == "listed_only_excluded_from_acquisition_and_presets"
    errors << "#{game}: numeric defaults mismatch" unless campaign.dig("time", "use_default") == [49, 35, 35, 30, 30] && campaign.dig("motion", "use_default") == 380
    errors << "#{game}: numeric offsets mismatch" unless campaign.dig("time", "base_offsets") == [10, 12, 14, 16, 18] && campaign.dig("motion", "base_offset") == 26
    observation_path = ROOT / campaign.fetch("evidence")
    if observation_path.file?
      errors << "#{game}: reduced campaign summary changed" unless Digest::SHA256.file(observation_path).hexdigest == campaign["sha256"]
      observed = JSON.parse(observation_path.read)
      %w[time motion country calibration].each do |field|
        errors << "#{game}: reduced campaign #{field} differs from evidence" unless campaign[field] == observed[field]
      end
    end
  end

  if (phase = data["phase1_documentation"])
    errors << "#{game}: Phase 1 must document eight operator settings" unless labelled_rows(data["menus"]).length == 8
    errors << "#{game}: calibration scope mismatch" unless data.dig("menus", "volume_setting", "policy") == "Listed Only; No Endpoint Acquisition"
    phase2_status = phase["phase2"]
    allowed_phase2 = %w[pending_script_and_acquisition_from_completed_inventory complete_recipe_generated_campaign_running acquisition_and_native_reload_validated]
    errors << "#{game}: invalid Phase 2 status" unless allowed_phase2.include?(phase2_status)
    if phase2_status != "pending_script_and_acquisition_from_completed_inventory"
      core_campaign = data.fetch("target_core_campaign", {})
      errors << "#{game}: Phase 2 manifest/status mismatch" unless core_campaign["status"] == phase2_status && core_campaign["planned_stages"] == 49
    end
    evidence = ROOT / phase.fetch("evidence")
    if evidence.file?
      errors << "#{game}: Phase 1 evidence changed" unless Digest::SHA256.file(evidence).hexdigest == phase["sha256"]
      documented = JSON.parse(evidence.read)
      errors << "#{game}: Phase 1 setting rows differ" unless data.dig("menus", "game_assignments", "options") == documented.dig("sets", game, "settings")
      errors << "#{game}: Phase 1 root differs" unless phase["root_menu"] == documented.dig("sets", game, "root_menu")
      documented["files"].each do |relative, hash|
        image = ROOT / relative
        errors << "#{game}: missing/changed Phase 1 image #{relative}" unless image.file? && Digest::SHA256.file(image).hexdigest == hash
      end
    end
  end

  actual = visible_rows(data, catalog)
  if actual.length != expected.length
    errors << "#{game}: #{actual.length} YAML rows, #{expected.length} catalog rows"
    next
  end

  actual.zip(expected).each_with_index do |(row, reference), index|
    unless normalized(row["label"]) == normalized(reference[:label])
      errors << "#{game} row #{index + 1}: #{row['label'].inspect} != #{reference[:label].inspect}"
      next
    end

    default = row["native_default"] || row["default"] || row["observed_native_value"]
    if default && normalized(rendered(default)) != normalized(reference[:default])
      errors << "#{game}:#{row['key']} default #{rendered(default).inspect} != #{reference[:default].inspect}"
    end

    next unless row["values"].is_a?(Array)
    expected_values = documented_values(reference[:values])
    next if expected_values.empty?
    yaml_values = row["values"].map { |value| normalized(rendered(value)) }.to_set
    catalog_values = expected_values.map { |value| normalized(value) }.to_set
    unless yaml_values == catalog_values
      errors << "#{game}:#{row['key']} values differ from the catalog"
    end
  end
  checked += 1
end

abort errors.join("\n") unless errors.empty?
puts "Diagnostic YAML audit passed: #{checked} files match #{CATALOG_PATH.basename}"
