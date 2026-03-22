[out:json][timeout:30];
area["name:en"="Zurich"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;