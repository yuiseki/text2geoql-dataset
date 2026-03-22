[out:json][timeout:30];
area["name:en"="Lisbon"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;