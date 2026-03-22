[out:json][timeout:30];
area["name:en"="Singapore"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;