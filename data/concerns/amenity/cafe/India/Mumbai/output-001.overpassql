[out:json][timeout:30];
area["name:en"="Mumbai"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;