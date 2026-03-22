[out:json][timeout:30];
area["name:en"="Ulsan"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;