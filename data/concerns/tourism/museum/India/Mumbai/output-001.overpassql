[out:json][timeout:30];
area["name:en"="Mumbai"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;