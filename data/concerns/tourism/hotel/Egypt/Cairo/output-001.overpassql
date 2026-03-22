[out:json][timeout:30];
area["name:en"="Cairo"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;