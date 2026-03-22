[out:json][timeout:30];
area["name:en"="Colombo"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;