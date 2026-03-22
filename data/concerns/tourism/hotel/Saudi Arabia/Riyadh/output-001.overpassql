[out:json][timeout:30];
area["name:en"="Riyadh"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;