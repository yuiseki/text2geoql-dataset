[out:json][timeout:30];
area["name:en"="Auckland"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;