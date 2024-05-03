[out:json][timeout:30000];
area["name"="City of New York"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;
