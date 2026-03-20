[out:json][timeout:30];
area["name:en"="Municipality of Prizren"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;
