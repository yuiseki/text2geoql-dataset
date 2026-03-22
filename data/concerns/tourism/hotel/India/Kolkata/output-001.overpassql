[out:json][timeout:30];
area["name:en"="Kolkata"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;