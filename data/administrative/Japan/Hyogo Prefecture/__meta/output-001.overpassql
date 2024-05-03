[out:json][timeout:30000];
area["name:en"="Hyogo Prefecture"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=7](area.searchArea);
);
out meta;
