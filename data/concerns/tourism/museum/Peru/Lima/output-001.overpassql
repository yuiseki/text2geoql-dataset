[out:json][timeout:30];
area["name:en"="Lima"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;