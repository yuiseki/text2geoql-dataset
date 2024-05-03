[out:json][timeout:30000];
area["name:en"="Tokyo"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=7](area.searchArea);
);
out meta;
