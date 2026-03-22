[out:json][timeout:30];
area["name:en"="Kaohsiung"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;