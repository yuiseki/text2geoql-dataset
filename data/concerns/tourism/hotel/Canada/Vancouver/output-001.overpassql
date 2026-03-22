[out:json][timeout:30];
area["name:en"="Vancouver"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;