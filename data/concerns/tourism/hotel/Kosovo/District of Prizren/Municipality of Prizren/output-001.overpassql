[out:json][timeout:30000];
area["name:en"="Municipality of Prizren"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;
