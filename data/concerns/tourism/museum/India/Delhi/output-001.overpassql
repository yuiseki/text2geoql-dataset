[out:json][timeout:30];
area["name:en"="Delhi"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;