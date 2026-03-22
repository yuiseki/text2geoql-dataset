[out:json][timeout:30];
area["name:en"="Vancouver"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;